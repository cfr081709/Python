import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# --- User Inputs ---
print("== Hand-Propelled Glider Simulation ==")
rho = float(input("Air density (kg/m^3) [e.g., 1.225]: "))
velocity = float(input("Initial launch velocity (m/s): "))
area = float(input("Wing area (m^2): "))
CL = float(input("Lift coefficient (C_L): "))
CD = float(input("Drag coefficient (C_D): "))
weight = float(input("Glider weight (Newtons): "))
wind = float(input("Wind speed (m/s): "))

facing_wind = False
if wind != 0:
    facing_wind = input("Is the glider facing the wind? (y/n): ").lower() == 'y'

altitude_offset = float(input("Launch altitude (m): "))
export = input("Export flight data to CSV? (y/n): ").lower() == 'y'
if export:
    filename = input("Filename for CSV (no extension): ") + ".csv"

# --- Setup ---
thrust = 0  # No engine
wind_effect = wind if facing_wind else -wind
adjusted_velocity = velocity + wind_effect
mass = weight / 9.81

# --- Initial Forces ---
q = 0.5 * rho * adjusted_velocity ** 2
lift = q * area * CL
drag = q * area * CD
net_vertical = lift - weight
net_horizontal = thrust - drag

print("\n--- Initial Force Summary ---")
print(f"Lift:   {lift:.2f} N")
print(f"Drag:   {drag:.2f} N")
print(f"Net Vertical:   {net_vertical:.2f} N")
print(f"Net Horizontal: {net_horizontal:.2f} N")

# --- Simulation Settings ---
time_step = 1
total_time = 20  # short glider flight
vx = adjusted_velocity
vy = 0
altitude = altitude_offset
distance = 0
initial_altitude = altitude_offset

# --- Data Storage ---
distances, altitudes, vx_list, vy_list, times = [], [], [], [], []
stall_occurred = False
stall_threshold = 4.0  # m/s minimum safe flying speed

# --- Run Simulation ---
for t in range(0, total_time + 1, time_step):
    if altitude <= 0 and t != 0:
        print(f"\n🛬 Glider landed at t = {t}s, distance = {distance:.1f} m.")
        break

    q = 0.5 * rho * vx ** 2
    lift = q * area * CL
    drag = q * area * CD

    ay = (lift - weight) / mass
    ax = (thrust - drag) / mass

    vy += ay * time_step
    vx += ax * time_step
    vx = max(vx, 0)  # No reverse motion

    altitude += vy * time_step
    distance += vx * time_step

    if vx < stall_threshold and not stall_occurred:
        print(f"\n⚠️ Stall Warning: Airspeed dropped below {stall_threshold} m/s at t = {t}s")
        stall_occurred = True

    times.append(t)
    distances.append(distance)
    altitudes.append(max(altitude, 0))
    vx_list.append(vx)
    vy_list.append(vy)

# --- Glide Ratio ---
altitude_loss = initial_altitude - altitudes[-1]
glide_ratio = distance / altitude_loss if altitude_loss > 0 else 0
print(f"\n🪂 Glide Ratio: {glide_ratio:.2f} (distance/altitude loss)")

# --- CSV Export ---
if export:
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Distance (m)", "Altitude (m)", "Vx (m/s)", "Vy (m/s)"])
        for i in range(len(times)):
            writer.writerow([times[i], distances[i], altitudes[i], vx_list[i], vy_list[i]])
    print(f"✅ Data exported to {filename}")

# --- Plot Setup ---
fig, axs = plt.subplots(1, 3, figsize=(16, 5))
ax1, ax2, ax3 = axs

def animate(i):
    ax1.clear()
    ax2.clear()
    ax3.clear()

    # Altitude vs Distance
    ax1.plot(distances[:i+1], altitudes[:i+1], color='blue')
    ax1.set_title("Altitude vs Distance")
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Altitude (m)")
    ax1.grid(True)
    if altitudes[i] <= 0 and i != 0:
        ax1.plot(distances[i], altitudes[i], 'ro', label="Landing")
        ax1.legend()

    # Vx vs Time
    ax2.plot(times[:i+1], vx_list[:i+1], color='green')
    ax2.set_title("Forward Speed (Vx) vs Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Vx (m/s)")
    ax2.grid(True)

    # Altitude vs Time
    ax3.plot(times[:i+1], altitudes[:i+1], color='purple')
    ax3.set_title("Altitude vs Time")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Altitude (m)")
    ax3.grid(True)

ani = FuncAnimation(fig, animate, frames=len(times), interval=400, repeat=False)
plt.tight_layout()
plt.show()
