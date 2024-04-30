import numpy as np

# Initialize parameters
alpha = 0.24  # cm^2/s, thermal diffusivity of air
dt = 2.5  # s, time step
dx = 20  # cm, space step
k = i = j = 1  # coordinates of the center point

# Initialize the temperature grid
temp = np.full((3, 3, 3), 5)  # 3D grid filled with 5°C
temp[k, i, j] = 4  # center point temperature is 4°C

# Calculate temperature change at the center point
delta_T = alpha * dt / dx**2 * (
    temp[k-1, i, j] + temp[k+1, i, j] +
    temp[k, i-1, j] + temp[k, i+1, j] +
    temp[k, i, j-1] + temp[k, i, j+1] -
    6 * temp[k, i, j]
)
print(delta_T)
# Update the temperature at the center point
temp[k, i, j] += delta_T
print(temp[k, i, j])
print(f"The temperature at the center point after {dt} seconds is {temp[k, i, j]:.5f} °C")
