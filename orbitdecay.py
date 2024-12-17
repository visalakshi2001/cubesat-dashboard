import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


# Atmospheric density function based on altitude (in meters)
def atmospheric_density(x, H):
    rho0 = 6e-10  # Reference density at h_ref = 175 km
    h_ref = 175e3  # Reference altitude (m)
    return rho0 * np.exp(-(x - h_ref) / H)


def plot_decay_graph():

    ###########################################################################

    # Mission variables
    initial_altitude = 450  # Initial altitude in km

    # Cubesat Variables
    A = 0.02  # Cross-sectional area in m^2 (example)
    m = 2  # Mass of satellite in kg (example)

    #############################################################################

    # Constants
    R_earth = 6371  # Radius of Earth in km
    G = 6.67430e-11  # Gravitational constant in m^3 kg^-1 s^-2
    M = 5.972e24  # Mass of Earth in kg
    Cd = 2.2  # Drag coefficient (dimensionless)
    H = 30000  # Scale height in meters for the atmosphere

    # Initial conditions
    r_earth = R_earth * 1000  # Radius of Earth in meters
    r_initial = (R_earth + initial_altitude) * 1000  # Initial distance from Earth's center in meters

    # Time initialization
    dt = 300  # Time step in seconds (5 minutes)
    total_time = 0  # Total time of the simulation in seconds
    altitudes = []  # List to store altitude vs time
    times = []  # List to store times

    # Convert initial conditions to meters and seconds
    r = r_initial  # Distance from Earth's center in meters

    # Calculate effective area
    Aeff = A*Cd

    # Calculate constant
    k = np.sqrt(G*M) * Aeff / m

    # Simulation loop
    while r > r_earth:  # Stop when altitude reaches 0 km (i.e., r reaches Earth's radius)
        # Calculate atmospheric density at current altitude
        alt = r-r_earth
        
        # Calculate air density at altitude
        rho = atmospheric_density(alt, H)  # Atmospheric density in kg/m^3

        # Calculate change in orbital radius over time period
        dr = -k * np.sqrt(r) * rho * dt

        # Update altitude based on velocity: dr = v * dt
        r = r + dr

        # Ensure that the altitude doesn't go below Earth's surface
        if r < r_earth:
            r = r_earth  # Set to Earth's surface

        # Store results for plotting
        total_time += dt
        altitudes.append((r-r_earth) / 1000)  # Convert meters to km
        times.append(total_time / (60 * 60 * 24 * 365))  # Convert seconds to days
    
    fig = px.line(x=times, y=altitudes, title='Orbital Decay of Cubesat')

    fig.update_layout(xaxis_title="Time (years)", yaxis_title="Altitude (km)")

    # # Plot the results after the simulation is complete
    # plt.figure(figsize=(10, 6))
    # plt.plot(times, altitudes, label="Altitude vs Time")
    # plt.xlabel('Time (years)')
    # plt.ylabel('Altitude (km)')
    # plt.title('Orbital Decay of Cubesat')
    # plt.grid(True)
    # plt.legend()
    # plt.show()

    return fig