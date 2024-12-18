
import streamlit as st
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from orbithelper import (plot_decay_graph, get_orbit_parameters,  
                        GetPositionVectors, plotly_orbit_plotter)

from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from poliastro.bodies import *


@st.cache_resource(show_spinner=False)
def orbitfunc():
    st.subheader("Orbital Details", divider="violet")

    attractor = Earth

    initial_orbit = get_orbit_parameters(
            attractor, "CubeSatOrbit", altitude=465.0
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

    cols = st.columns(2)
    # st.dataframe(orbits_df.T, use_container_width=True)

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


    with cols[0]:
        fig1 = plotly_orbit_plotter(
            orbits.values(),
            attractor,
            labels=orbits.keys(),
            positions=positions
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with cols[1]:
        with st.expander("CubeSat Orbit Details", expanded=True):
            st.dataframe(orbits_df.T, use_container_width=True)
        fig = plot_decay_graph()
        st.pyplot(fig, use_container_width=True)

    
    

 
