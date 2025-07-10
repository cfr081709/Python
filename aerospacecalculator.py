import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# --- User Inputs ---
rho = float(input("Enter air density (kg/m^3): "))
velocity = float(input("Enter initial velocity (m/s): "))
area = float(input("Enter wing area (m^2): "))
CL = float(input("Enter lift coefficient (C_L): "))
CD = float(input("Enter drag coefficient (C_D): "))
thrust = float(input("Enter thrust (Newtons): "))
weight = float(input("Enter aircraft weight (Newtons): "))
wind = float(input("Enter wind speed (m/s): "))
facing_wind = input("Are you facing the wind? (y/n): ").lower() == 'y'
altitude_offset = float(input("Enter starting altitude (m): "))
export = input("Export data to CSV? (y/n): ").lower() == 'y'
if export == 'y':
    filename = input("Enter filename for CSV export (without extension): ") + ".csv"

# --- Setup values ---
wind_effect = wind if facing_wind else -wind
adjusted_velocity = velocity + wind_effect
mass = weight / 9.81

# --- Recalculate based on adjusted velocity ---
q = 0.5 * rho * adjusted_velocity ** 2
lift = q * area * CL
drag = q * area * CD

# --- Forces summary ---
net_vertical = lift - weight
net_horizontal = thrust - drag

# --- Print Summary Info ---
print("\n--- Force Summary ---")
print(f"Lift:   {lift:.2f} N")
print(f"Drag:   {drag:.2f} N")
print(f"Thrust: {thrust:.2f} N")
print(f"Net Vertical Force:   {net_vertical:.2f} N")
print(f"Net Horizontal Force: {net_horizontal:.2f} N")


# --- Time Simulation Settings ---
time_step = 1
total_time = 30  # seconds
vx = adjusted_velocity
vy = 0
altitude = altitude_offset
distance = 0

# --- Data Lists ---
distances = []
altitudes = []
vx_list = []
vy_list = []
times = []

#--- Export Data to CSV if requested ---
if export == 'y':

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write header with clear names
        writer.writerow([
            "Time (s)",
            "Horizontal Distance (m)",
            "Altitude (m)",
            "Forward Velocity (Vx) [m/s]",
            "Climb Rate (Vy) [m/s]"
        ])
    
        # Write each row of time-step data
        for i in range(len(times)):
            writer.writerow([
                times[i],
                distances[i],
                altitudes[i],
                vx_list[i],
                vy_list[i]
            ])

        print(f"\n✅ Flight data exported as: {filename}")

# --- Run Simulation ---
landed = False
for t in range(0, total_time + 1, time_step):
    if altitude <= 0 and t != 0:
        print(f"\n🛬 Aircraft has landed at t = {t}s, distance = {distance:.1f} m.")
        landed = True
        break

    ay = (lift - weight) / mass
    ax = (thrust - drag) / mass

    vy += ay * time_step
    vx += ax * time_step

    altitude += vy * time_step
    distance += vx * time_step

    # Store data
    distances.append(distance)
    altitudes.append(max(altitude, 0))
    vx_list.append(vx)
    vy_list.append(vy)
    times.append(t)

# --- Plot Setup ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
(ax1, ax2), (ax3, ax4) = axs

def animate(i):
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    # Flight Path
    ax1.plot(distances[:i+1], altitudes[:i+1], color='blue', linewidth=2)
    ax1.set_title("Altitude vs Distance")
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Altitude (m)")
    ax1.grid(True)

    if altitudes[i] <= 0 and i != 0:
        ax1.plot(distances[i], altitudes[i], 'ro', markersize=8, label="Landing Point")
        ax1.legend()

    # Horizontal Velocity
    ax2.plot(times[:i+1], vx_list[:i+1], color='green', linewidth=2)
    ax2.set_title("Forward Speed (Vx) vs Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Vx (m/s)")
    ax2.grid(True)

    # Vertical Velocity
    ax3.plot(times[:i+1], vy_list[:i+1], color='orange', linewidth=2)
    ax3.set_title("Climb Rate (Vy) vs Time")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Vy (m/s)")
    ax3.grid(True)

    # Altitude over Time
    ax4.plot(times[:i+1], altitudes[:i+1], color='purple', linewidth=2)
    ax4.set_title("Altitude vs Time")
    ax4.set_xlabel("Time (s)")
    ax4.set_ylabel("Altitude (m)")
    ax4.grid(True)

# Create animation
ani = FuncAnimation(fig, animate, frames=len(times), interval=400, repeat=False)
plt.tight_layout()
plt.show()
