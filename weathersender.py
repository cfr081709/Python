import requests
import smtplib
import sys
import schedule
import time
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# === Load Environment Variables ===
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
EMAIL = os.getenv("GMAIL_ADDRESS")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# === Supported Carriers ===
CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
}

def get_location():
    """Get user's city and country based on IP."""
    try:
        location_data = requests.get("https://ipinfo.io").json()
        city = location_data.get("city")
        country = location_data.get("country")
        return city, country
    except Exception as e:
        print("Error getting location:", e)
        return None, None

def get_weather(city, country):
    """Get current weather from WeatherAPI."""
    if not city or not country:
        print("Invalid location data.")
        return None

    location_query = f"{city},{country}"
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={location_query}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Weather API error:", response.status_code, response.text)
        return None

def send_message(phone_number, carrier, message):
    """Send SMS via email-to-SMS gateway."""
    if carrier not in CARRIERS:
        print(f"⚠️ Unsupported carrier: {carrier}. Supported: {', '.join(CARRIERS.keys())}")
        return False

    recipient = f"{phone_number}{CARRIERS[carrier]}"

    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = "Weather Update"
        msg['From'] = EMAIL
        msg['To'] = recipient

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Message sent to {phone_number} ({carrier})")
        return True
    except Exception as e:
        print("Error sending message:", e)
        return False

def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <PHONE_NUMBER> <CARRIER>")
        print(f"Supported carriers: {', '.join(CARRIERS.keys())}")
        sys.exit(1)

    phone_number = sys.argv[1]
    carrier = sys.argv[2].lower()

    city, country = get_location()
    weather_data = get_weather(city, country)

    if weather_data:
        loc = weather_data['location']
        current = weather_data['current']

        message = (
            f"📍 Location: {loc['name']}, {loc['region']}, {loc['country']}\n"
            f"🌡️ Temp: {current['temp_f']}°F (Feels like: {current['feelslike_f']}°F)\n"
            f"🌥️ Condition: {current['condition']['text']}\n"
            f"💧 Humidity: {current['humidity']}%"
        )

        send_message(phone_number, carrier, message)
    else:
        print("Failed to retrieve weather data.")

def schedule_daily_weather(phone_number, carrier, send_time="06:00"):
    """Schedule daily weather SMS at specified time (HH:MM)."""
    def job():
        city, country = get_location()
        weather_data = get_weather(city, country)

        if weather_data:
            loc = weather_data['location']
            current = weather_data['current']

            message = (
                f"📍 Location: {loc['name']}, {loc['region']}, {loc['country']}\n"
                f"🌡️ Temp: {current['temp_f']}°F (Feels like: {current['feelslike_f']}°F)\n"
                f"🌥️ Condition: {current['condition']['text']}\n"
                f"💧 Humidity: {current['humidity']}%"
            )
            send_message(phone_number, carrier, message)
        else:
            print("Failed to retrieve weather data.")

    schedule.every().day.at(send_time).do(job)
    print(f"⏰ Scheduler running: daily at {send_time}")

    while True:
        schedule.run_pending()
        time.sleep(30)

# === Entry Point ===
# Uncomment for command-line run:
# if __name__ == "__main__":
#     main()

# Uncomment to schedule daily messages:
# schedule_daily_weather("YOUR_PHONE_NUMBER", "YOUR_CARRIER", send_time="06:00")
