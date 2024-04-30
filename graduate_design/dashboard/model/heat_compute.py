import numpy as np

# Initialize parameters
alpha = 0.24  # cm^2/s, thermal diffusivity of air
dt = 2.5  # s, time step
dx = 20  # cm, space step

# Initialize the temperature of the points
temp_high = 4  # °C
temp_mid = temp_low = 6  # °C

# Calculate temperature change at the high point
delta_T_high = alpha * dt / dx**2 * (temp_mid - temp_high)

# Calculate temperature change at the mid point
delta_T_mid = alpha * dt / dx**2 * ((temp_high - temp_mid) + (temp_low - temp_mid))

# Calculate temperature change at the low point
delta_T_low = alpha * dt / dx**2 * (temp_mid - temp_low)

# Update the temperature at the points
temp_high += delta_T_high
temp_mid += delta_T_mid
temp_low += delta_T_low

print(f"The temperature at the high point after {dt} seconds is {temp_high:.4f} °C")
print(f"The temperature at the mid point after {dt} seconds is {temp_mid:.4f} °C")
print(f"The temperature at the low point after {dt} seconds is {temp_low:.4f} °C")
