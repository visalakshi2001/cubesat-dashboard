
import streamlit as st
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from PIL import Image

import datetime
from poliastro.bodies import (Earth,Moon,Mars,Jupiter,Saturn)
from poliastro.bodies import *
from poliastro.twobody import Orbit
from poliastro.core.elements import coe2rv
from astropy.time import Time

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

@st.cache_data()
def orbitfunc():
    st.title("Orbit")

    planets = define_main_attractors()

    attractor = planets["Earth"]

    initial_orbit = get_orbit_parameters(
            attractor, "CubeSatOrbit", altitude=342.0
        )
    initial_orbit = Orbit.from_classical(
            initial_orbit[0], # attractor
            initial_orbit[1], # semi-major axis
            initial_orbit[2], # eccentricity
            initial_orbit[3], # inclination
            initial_orbit[4], # raan
            initial_orbit[5], # argp
            initial_orbit[6], # nu
            # initial_orbit[7], # epoch
        )
    
    orbits = {"CubeSat Orbit" : initial_orbit}


    orbits_df = pd.DataFrame(
        {
            "Semi-major axis (km)": [orbit.a.to(u.km).value for orbit in orbits.values()],
            "Eccentricity": [orbit.ecc.value for orbit in orbits.values()],
            "Periapsis from surface (km)": [(orbit.a.to(u.km).value * (1 - orbit.ecc.value) - attractor.R.to(u.km).value) for orbit in orbits.values()],
            "Apoapsis from surface (km)": [(orbit.a.to(u.km).value * (1 + orbit.ecc.value) - attractor.R.to(u.km).value) for orbit in orbits.values()],
            "Inclination (deg)": [orbit.inc.to(u.deg).value for orbit in orbits.values()],
            "RAAN (deg)": [orbit.raan.to(u.deg).value for orbit in orbits.values()],
            "Argument of periapsis (deg)": [
                orbit.argp.to(u.deg).value for orbit in orbits.values()
            ],
            "True anomaly (deg)": [orbit.nu.to(u.deg).value for orbit in orbits.values()],
            "Period (s)": [orbit.period.to(u.s).value for orbit in orbits.values()],
            # "Epoch": [orbit.epoch.iso for orbit in orbits.values()],
        },
        index=orbits.keys(),
    )
    st.dataframe(orbits_df.T, use_container_width=True)

    # Create an instance of OrbitElements
    initial_orbit_elements = GetPositionVectors(initial_orbit)
    # Get position and velocity at periapsis of initial orbit (0 degrees true anomaly)
    nu_periapsis_initial = 0 * u.deg
    position_periapsis_initial, velocity_periapsis_initial = initial_orbit_elements.get_position_velocity(nu_periapsis_initial)

    # Get position and velocity at apoapsis of initial orbit (180 degrees true anomaly)
    nu_apoapsis_initial = 180 * u.deg
    position_apoapsis_initial, velocity_apoapsis_initial = initial_orbit_elements.get_position_velocity(nu_apoapsis_initial)

    # Calculate absolute velocity at point
    velocity_periapsis_initial_abs = np.linalg.norm(velocity_periapsis_initial)
    velocity_apoapsis_initial_abs = np.linalg.norm(velocity_apoapsis_initial)

    positions = {
        "I Periapsis": position_periapsis_initial,
        "I Apoapsis": position_apoapsis_initial,
    }


    st.subheader("Orbits projection:")
    fig1 = plotly_orbit_plotter(
        orbits.values(),
        attractor,
        labels=orbits.keys(),
        positions=positions
    )
    st.plotly_chart(fig1, use_container_width=True)

    


# ###########################################################
# ######### HELPER FUNCTIONS FOR ORBIT CREATION #############
# ###########################################################

# def get_mission_epoch():
#     """Returns the mission epoch."""
#     now = datetime.datetime.now()
#     date = st.sidebar.date_input("Select the mission epoch", value=now)
#     time = st.sidebar.time_input("Select the mission epoch time", value=now.time())
#     date = datetime.datetime(
#         date.year, date.month, date.day, time.hour, time.minute, time.second
#     )
#     return Time(date, scale="utc")

@st.cache_data()
def define_main_attractors():
    """Returns a dictionary of the main attractors in the solar system."""
    return {
        "Earth": Earth,
        "Moon": Moon,
        "Mars": Mars,
        "Jupiter": Jupiter,
        "Saturn": Saturn,
        "Uranus": Uranus,
        "Neptune": Neptune,
        "Pluto": Pluto,
        "Mercury": Mercury,
        "Venus": Venus,
        "Sun": Sun,
    }

@st.cache_data()
def semimajor_axis_from_periapsis(periapsis, eccentricity, attractor_radius):
    """
    Calculate the semi-major axis of an orbit from its periapsis distance and eccentricity.

    Parameters:
    periapsis (float): The periapsis distance (in kilometers)
    eccentricity (float): The eccentricity of the orbit (dimensionless)

    Returns:
    float: The semi-major axis (in kilometers)
    """

    # Convert the periapsis distance to meters
    periapsis_m = periapsis * 1000.0
    periapsis_distance = periapsis_m + attractor_radius

    # Calculate the semi-major axis
    semi_major_axis_m = periapsis_distance / (1.0 - eccentricity)

    # Convert the semi-major axis back to kilometers
    semi_major_axis_km = semi_major_axis_m / 1000.0

    return semi_major_axis_km


@st.cache_data()
def get_orbit_parameters(_attractor, orbit_name, altitude=500.0, ecc=0.0, inclination=45.0, raan=0.0, argp=0.0, nu=0.0):
    """Returns the orbit parameters for a given orbit name."""
    # define any orbit based on streamlit inputs for all orbit parameters
    # orbit_periapsis = st.number_input(
    #     "Orbit periapsis altitude [km]",
    #     min_value=0.0,
    #     value=altitude,
    #     step=50.0,
    #     key=f"{orbit_name}_altitude",
    #     help="Altitude of the orbit above the Planet's surface (counted from equatorial radius).",
    # )
    
    # orbit_ecc = st.number_input(
    #     "Orbit eccentricity",
    #     min_value=0.0,
    #     max_value=1.0,
    #     value=ecc,
    #     step=0.01,
    #     key=f"{orbit_name}_ecc",
    #     help="Eccentricity of the orbit is the ratio of the distance between the two foci of the ellipse and the distance between the center of the ellipse and one of the foci. For more information, see https://en.wikipedia.org/wiki/Eccentricity_(mathematics)",
    # )
    # orbit_a = semimajor_axis_from_periapsis(orbit_periapsis,orbit_ecc, attractor.R.to(u.m).value)
    # orbit_inclination = st.number_input(
    #     "Orbit inclination [deg]",
    #     min_value=0.0,
    #     max_value=180.0,
    #     value=inclination,
    #     step=1.0,
    #     key=f"{orbit_name}_inclination",
    #     help="Inclination of the orbit with respect to the equatorial plane of the Planet. 0.0 for equatorial orbits, 90.0 for polar orbits.",
    # )
    # orbit_raan = st.number_input(
    #     "Orbit RAAN [deg]",
    #     min_value=0.0,
    #     max_value=360.0,
    #     value=raan,
    #     step=1.0,
    #     key=f"{orbit_name}_raan",
    #     help="The Right Ascension of the Ascending Node of the trajectory orbit is the angle between the ascending node and the vernal equinox. For more information, see https://en.wikipedia.org/wiki/Right_ascension_of_the_ascending_node.",
    # )
    # orbit_argp = st.number_input(
    #     "Orbit argument of perigee [deg]",
    #     min_value=0.0,
    #     max_value=360.0,
    #     value=argp,
    #     step=1.0,
    #     key=f"{orbit_name}_argp",
    #     help="The argument of perigee is the angle between the ascending node and the perigee. For more information, see https://en.wikipedia.org/wiki/Argument_of_perigee.",
    # )
    # orbit_nu = st.number_input(
    #     "Orbit true anomaly [deg]",
    #     min_value=0.0,
    #     max_value=360.0,
    #     value=nu,
    #     step=1.0,
    #     key=f"{orbit_name}_nu",
    #     help="The true anomaly is the angle between the perigee and the spacecraft. For more information, see https://en.wikipedia.org/wiki/True_anomaly.",
    # )

    # altitude of 465km (SMA = 6378+465)
    orbit_periapsis = 465
    orbit_ecc = 0
    orbit_a = semimajor_axis_from_periapsis(orbit_periapsis,orbit_ecc, _attractor.R.to(u.m).value)
    orbit_inclination = 45
    orbit_raan = 10
    orbit_argp = 0
    orbit_nu = nu

    orbit_name = (
        _attractor,
        orbit_a * u.km,
        orbit_ecc * u.one,
        orbit_inclination * u.deg,
        orbit_raan * u.deg,
        orbit_argp * u.deg,
        orbit_nu * u.deg,
        # mission_epoch,
    )

    # return orbit
    return orbit_name

@st.cache_data()
def plotly_orbit_plotter(_orbit_list, attractor, positions=None, labels=None):
    """
    Plots a list of orbits in 3D using plotly.
    Parameters:
    orbit_list: list of poliastro.twobody.orbit.Orbit
        List of orbits to plot
    attractor: poliastro.bodies.Body
        Main attractor of the orbits
    maneuvers: list of tuples
        List of tuples containing maneuver impulse data in the format (Orbit, time, delta-v)
    labels: list of str
        List of labels for the orbits
    Returns:
    fig: plotly.graph_objects.Figure
    Help received from this thread: https://community.plotly.com/t/applying-full-color-image-texture-to-create-an-interactive-earth-globe/60166
    """
    fig = make_subplots(rows=1, cols=1, specs=[[{"type": "scatter3d"}]])

    if labels is None:
        labels = ["Orbit"] * len(_orbit_list)

    for orbit, label in zip(_orbit_list, labels):
        r = orbit.sample().xyz.T
        x, y, z = r[:, 0].to(u.km).value, r[:, 1].to(u.km).value, r[:, 2].to(u.km).value
        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                name=label,
                
            )
        )

    if positions is not None:
        for pos_label, pos_data in positions.items():
            x, y, z = pos_data[0].to(u.km).value, pos_data[1].to(u.km).value, pos_data[2].to(u.km).value
            fig.add_trace(
                go.Scatter3d(
                    x=[x],
                    y=[y],
                    z=[z],
                    mode="markers+text",
                    marker=dict(size=8, opacity=1),
                    text=[pos_label],
                    textposition="bottom center",
                    showlegend=True,
                    name=pos_label, # add legend for each position marker
                )
            )

    # Add attractor
    texture = np.asarray(Image.open('images/temp.jpeg')).T
    u_rad = u.km
    N_lat = int(texture.shape[0])
    N_lon = int(texture.shape[1])
    thetas = np.linspace(0, 2 * np.pi, N_lat)
    phis = np.linspace(0, np.pi, N_lon)
    radius_equatorial = attractor.R.to(u_rad).value
    if attractor.R_polar is None:
        radius_polar = radius_equatorial
    else:
        radius_polar = attractor.R_polar.to(u_rad).value
    
    
    x_center = radius_equatorial * np.outer(np.cos(thetas), np.sin(phis))
    y_center = radius_equatorial * np.outer(np.sin(thetas), np.sin(phis))
    z_center = radius_polar * np.outer(np.ones(N_lat),np.cos(phis))
    colorscale =[[0.0, 'rgb(30, 59, 117)'],

                 [0.1, 'rgb(46, 68, 21)'],
                 [0.2, 'rgb(74, 96, 28)'],
                 [0.3, 'rgb(115,141,90)'],
                 [0.4, 'rgb(122, 126, 75)'],

                 [0.6, 'rgb(122, 126, 75)'],
                 [0.7, 'rgb(141,115,96)'],
                 [0.8, 'rgb(223, 197, 170)'],
                 [0.9, 'rgb(237,214,183)'],

                 [1.0, 'rgb(255, 255, 255)']]

    fig.add_trace(
        go.Surface(
            x=x_center, 
            y=y_center, 
            z=z_center, 
            surfacecolor=texture,
            colorscale=colorscale, 
            showscale=False
        )
    )

    fig.update_layout(scene=dict(aspectmode="data"))
    fig.update_layout(height=800, legend=dict(x=0, y=1, orientation="h"))

    return fig


# def generate_earth_map_points(resolution=50):
#     """
#     Generates latitude and longitude points for Earth's continents using cartopy.
#     """
#     proj = ccrs.PlateCarree()
#     fig, ax = plt.subplots(subplot_kw={'projection': proj}, dpi=resolution)
#     ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    
#     # Extract contour coordinates
#     points = []
#     for collection in ax.collections:
#         for path in collection.get_paths():
#             for segment in path.to_polygons():
#                 lon, lat = segment[:, 0], segment[:, 1]
#                 points.append((lon, lat))
#     plt.close(fig)
#     return points

    


# def plot_earth_with_continents(fig, attractor, radius):
#     """
#     Plot Earth as a sphere with dynamic continent outlines generated via Cartopy.
#     """
#     thetas = np.linspace(0, 2 * np.pi, 100)
#     phis = np.linspace(0, np.pi, 50)
#     x_center = radius * np.outer(np.cos(thetas), np.sin(phis))
#     y_center = radius * np.outer(np.sin(thetas), np.sin(phis))
#     z_center = radius * np.outer(np.ones_like(thetas), np.cos(phis))
    
#     # Add sphere
#     fig.add_surface(
#         x=x_center, y=y_center, z=z_center,
#         colorscale=[[0, "rgb(0, 128, 255)"], [1, "rgb(0, 0, 128)"]],
#         opacity=0.8,
#         showscale=False,
#     )
    
#     # Add continent outlines
#     earth_points = generate_earth_map_points()
#     for lon, lat in earth_points:
#         x = radius * np.cos(np.radians(lat)) * np.cos(np.radians(lon))
#         y = radius * np.cos(np.radians(lat)) * np.sin(np.radians(lon))
#         z = radius * np.sin(np.radians(lat))
        
#         fig.add_scatter3d(
#             x=x, y=y, z=z,
#             mode="lines",
#             line=dict(color="black", width=1),
#             showlegend=False
#         )

class GetPositionVectors:
    def __init__(self, orbit):
        self.a = orbit.a
        self.ecc = orbit.ecc
        self.inc = orbit.inc
        self.raan = orbit.raan
        self.argp = orbit.argp
        self.body = orbit.attractor
        self.k = orbit.attractor.k.to(u.km**3 / u.s**2)  # Gravitational parameter in km^3/s^2
        self.p = (self.a * (1 - self.ecc**2)).to(u.km)  # Semi-latus rectum in km

    def get_position_velocity(self, nu):
        '''
        Return the position and velocity vector for any orbit.
        '''
        r_ijk, v_ijk = coe2rv(self.k, self.p, self.ecc.value, self.inc.to(u.rad).value,
                              self.raan.to(u.rad).value, self.argp.to(u.rad).value, nu.to(u.rad).value)

        position = r_ijk * u.km
        velocity = v_ijk * u.km / u.s

        return position, velocity
    
    def get_periapsis_apoapsis_positions(self):
        '''
        Return the position and velocity vector for periapsis and apoapsis of any given orbit.
        '''
        nu_periapsis = 0 * u.deg
        position_periapsis, _ = self.get_position_velocity(nu_periapsis)

        nu_apoapsis = 180 * u.deg
        position_apoapsis, _ = self.get_position_velocity(nu_apoapsis)

        return position_periapsis, position_apoapsis
