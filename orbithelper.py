import numpy as np
import plotly.express as px
import pandas as pd

import streamlit as st
from plotly.subplots import make_subplots
from poliastro.bodies import *
import matplotlib.pyplot as plt
from poliastro.core.elements import coe2rv
from astropy.time import Time
import plotly.graph_objs as go
from PIL import Image


@st.cache_data(show_spinner=False)
def plot_decay_graph():


    decaydf = pd.read_csv('reports/decay.csv')
    times = decaydf['times'].values
    altitudes = decaydf['altitudes'].values
    
    fig = plt.figure(figsize=(12,5))
    ax = fig.add_subplot(111)
    
    ax.plot(times, altitudes, label="Altitude vs Time")
    plt.annotate("t_d=%0.2f years" % times[-1], xy=(1, times[-1]), xytext=(times[-1]-3.3,0))
    plt.xlabel('Time (years)')
    plt.ylabel('Altitude (km)')
    plt.title('Orbital Decay of Cubesat')
    plt.grid(True)
    plt.legend()


    return fig




# ORBIT PROJECTIONS


def plotly_orbit_plotter(orbit_list, attractor, positions=None, labels=None):
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
        labels = ["Orbit"] * len(orbit_list)

    for orbit, label in zip(orbit_list, labels):
        r = orbit.sample().xyz.T
        x, y, z = r[:, 0].to(u.km).value, r[:, 1].to(u.km).value, r[:, 2].to(u.km).value
        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                name=label,
                showlegend=True,
                line=dict(color='red', width=5)
            )
        )

        # fig.update_traces(
        #     # marker=dict(
        #     #     color='lightblue',
        #     #     size=10),
        #     line=dict(
        #         color='purple',
        #         width=12
        #     )
        # )

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
            showscale=False,
            hovertext='none',
            hovertemplate=None
        )
    )

    fig.update_layout(title_text="Orbit Projection",scene=dict(aspectmode="data"))
    fig.update_layout(height=800, legend=dict(x=0, y=1, orientation="h"))

    return fig

   


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
    # altitude of 465km (SMA = 6378+465)
    # "Orbit periapsis altitude [km]"
    # Altitude of the orbit above the Planet's surface (counted from equatorial radius).
    orbit_periapsis = 465

    # "Orbit eccentricity"
    # Eccentricity of the orbit is the ratio of the distance between the two foci of the ellipse and the distance between the center of the ellipse and one of the foci
    orbit_ecc = 0
    orbit_a = semimajor_axis_from_periapsis(orbit_periapsis,orbit_ecc, _attractor.R.to(u.m).value)

    # "Orbit inclination [deg]"
    # Inclination of the orbit with respect to the equatorial plane of the Planet. 0.0 for equatorial orbits, 90.0 for polar orbits."
    orbit_inclination = 45

    # "Orbit RAAN [deg]",
    # The Right Ascension of the Ascending Node of the trajectory orbit is the angle between the ascending node and the vernal equinox.
    orbit_raan = 10

    # "Orbit argument of perigee [deg]"
    # The argument of perigee is the angle between the ascending node and the perigee
    orbit_argp = 0

    # "Orbit true anomaly [deg]"
    # The true anomaly is the angle between the perigee and the spacecraft
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
    
