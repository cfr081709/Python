import requests
import re

# --- Config ---
AIRPORT = "KPYM"
METAR_URL = f"https://aviationweather.gov/api/data/metar?ids={AIRPORT}&format=raw"

# --- Helpers ---
def c_to_f(c):
    try:
        c_val = float(c.replace('M','-'))  # Handle negative temps e.g. M02 -> -2
        return round((c_val * 9 / 5) + 32, 1)
    except:
        return "N/A"

def decode_sky_conditions(codes):
    """
    Decode multiple sky layers, e.g. ['CLR'], ['SCT020', 'BKN050'], etc.
    Returns concatenated string describing layers.
    """
    codes_map = {
        'CLR': 'Clear',
        'SKC': 'Sky Clear',
        'FEW': 'Few clouds',
        'SCT': 'Scattered clouds',
        'BKN': 'Broken clouds',
        'OVC': 'Overcast',
        'BR': 'Mist',
        'FG': 'Fog',
        'HZ': 'Haze',
        'TS': 'Thunderstorms',
        'RA': 'Rain',
        '-RA': 'Light Rain',
        '+RA': 'Heavy Rain',
    }

    descriptions = []
    for code in codes:
        # Handle special intensity prefix for precipitation codes
        if code.startswith(('+', '-')):
            base_code = code[1:]
            intensity = code[0]
            label = codes_map.get(code)
            if label is None and base_code in codes_map:
                label = f"{'Light' if intensity == '-' else 'Heavy'} {codes_map[base_code]}"
            descriptions.append(label if label else "Unknown")
            continue

        match = re.match(r"([A-Z]{2,3})(\d{3})?", code)
        if match:
            layer, height = match.groups()
            label = codes_map.get(layer, "Unknown")
            if height:
                descriptions.append(f"{label} at {int(height)*100} ft")
            else:
                descriptions.append(label)
        else:
            descriptions.append("Unknown")
    return ", ".join(descriptions) if descriptions else "N/A"

def classify_flight_rules(visibility, sky_raw_list):
    try:
        vis_miles = float(re.findall(r"[\d.]+", visibility)[0])

        # Find ceiling from lowest broken or overcast layer
        ceilings = []
        for code in sky_raw_list:
            match = re.match(r"(BKN|OVC)(\d{3})", code)
            if match:
                ceilings.append(int(match.group(2)) * 100)
        ceiling_ft = min(ceilings) if ceilings else 9999

        if vis_miles >= 5 and ceiling_ft >= 3000:
            return "✅ VFR (Visual Flight Rules)"
        elif vis_miles >= 3 and ceiling_ft >= 1000:
            return "⚠️ MVFR (Marginal VFR)"
        elif vis_miles >= 1 and ceiling_ft >= 500:
            return "❌ IFR (Instrument Flight Rules)"
        else:
            return "🚨 LIFR (Low IFR)"
    except:
        return "Unknown"

# --- Parser ---
def parse_metar(metar):
    data = {}
    parts = metar.split()

    try:
        data['station'] = parts[0]

        # Observation time (UTC → EST)
        if len(parts) > 1:
            match = re.match(r"(\d{2})(\d{2})(\d{2})Z", parts[1])
            if match:
                day, hour, minute = map(int, match.groups())
                hour_est = (hour - 5) % 24
                data['obs_time'] = f"{day}th at {hour_est:02}:{minute:02} EST"
            else:
                data['obs_time'] = "Unknown"
        else:
            data['obs_time'] = "Unknown"

        # Wind (always parts[2])
        if len(parts) > 2:
            wind = parts[2]
            wind_match = re.match(r"(\d{3})(\d{2})(?:G\d+)?KT", wind)
            if wind_match:
                wind_dir, wind_spd = wind_match.groups()
                data['wind'] = f"{wind_dir}° at {wind_spd} kt"
            else:
                data['wind'] = "Unknown"
        else:
            data['wind'] = "Unknown"

        # Visibility (always parts[3])
        if len(parts) > 3:
            visibility_raw = parts[3]
            vis_match = re.match(r"(\d+)(SM)?", visibility_raw)
            if vis_match:
                vis_value = vis_match.group(1)
                vis_unit = vis_match.group(2) or ''
                data['visibility'] = f"{vis_value} {vis_unit}".strip()
            else:
                data['visibility'] = visibility_raw  # fallback
        else:
            data['visibility'] = "Unknown"

        # Sky conditions (from parts[4] up to temp/dew)
        sky_codes = []
        temp_dew_index = None
        for i in range(4, len(parts)):
            if '/' in parts[i]:
                temp_dew_index = i
                break
            else:
                sky_codes.append(parts[i])

        data['sky_raw'] = sky_codes
        data['sky_condition'] = decode_sky_conditions(sky_codes)

        # Temperature/Dew point
        if temp_dew_index is not None:
            temp_dew = parts[temp_dew_index]
            if '/' in temp_dew:
                temp, dew = temp_dew.split('/')
                data['temperature_c'] = f"{temp}°C"
                data['temperature_f'] = f"{c_to_f(temp)}°F"
                data['dew_point_c'] = f"{dew}°C"
                data['dew_point_f'] = f"{c_to_f(dew)}°F"
            else:
                data['temperature_c'] = data['temperature_f'] = "N/A"
                data['dew_point_c'] = data['dew_point_f'] = "N/A"
        else:
            data['temperature_c'] = data['temperature_f'] = "N/A"
            data['dew_point_c'] = data['dew_point_f'] = "N/A"

        # Altimeter (usually next part after temp/dew)
        altimeter_index = temp_dew_index + 1 if temp_dew_index is not None else None
        if altimeter_index is not None and altimeter_index < len(parts):
            altimeter = parts[altimeter_index]
            if altimeter.startswith("A"):
                pressure = float(altimeter[1:]) / 100
                data['pressure'] = f"{pressure:.2f} inHg"
            else:
                data['pressure'] = "Unknown"
        else:
            data['pressure'] = "Unknown"

        # Flight rules classification
        data['flight_rules'] = classify_flight_rules(data['visibility'], sky_codes)

    except Exception as e:
        data['error'] = f"Parsing error: {e}"

    return data

# --- Main ---
def main():
    print(f"Fetching METAR for {AIRPORT}...")
    response = requests.get(METAR_URL)

    if response.status_code == 200:
        lines = response.text.strip().splitlines()
        for line in lines:
            if line.strip():
                print("\nRaw METAR:")
                print(line)

                print("\nParsed Data:")
                parsed = parse_metar(line)
                for k, v in parsed.items():
                    if isinstance(v, list):
                        v = ', '.join(v)
                    print(f"{k.title().replace('_', ' ')}: {v}")
                break
    else:
        print("Failed to retrieve METAR. Status:", response.status_code)

if __name__ == "__main__":
    main()
