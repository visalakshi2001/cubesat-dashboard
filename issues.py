import streamlit as st

# ########## ISSUES VIEW FUNCTION
def sysissues():
    # create three columns of equal size
    top_cols = st.columns(3)

    # with the first column, create content for all the scheduling conflicts
    with top_cols[0]:
        # create an accordion expander using st.expander. this will contain all details of the conflict issues
        conflicts = st.expander("⚠️ Four tests have overlapping schedule", expanded=True)

        # call the expander and create containers for each occurring conflict.
        # this needs to be updated to a controlled loop, getting data from the OML query data
        with conflicts:
            with st.container(border=True):
                st.error("Pathway Creation Time Test has potential schedule conflict with other tests", icon="❗")
                st.markdown("<li>Test Names: Maneuvrability Test</li> \
                            <li>Scheduled Date and Time: September 1 12:00 - 13:00</li>  \
                            <li>Conflict Type: Has the same Site TE53_Environment</li>  \
                            ",True)
            with st.container(border=True):
                st.error("Maneuvrability Test has potential schedule conflict with other tests", icon="❗")
                st.markdown("<li>Test Names: Pathway Creation Time</li> \
                            <li>Scheduled Date and Time: September 1 12:00 - 13:00</li>  \
                            <li>Conflict Type: Has the same Site TE53_Environment</li>  \
                            ",True)
            with st.container(border=True):
                st.error("Path Confidence Test has potential schedule conflict with other tests", icon="❗")
                st.markdown("<li>Test Names: Information Loss Test</li> \
                            <li>Scheduled Date and Time: September 2 12:00 - 13:00</li>  \
                            <li>Conflict Type: Has the same Equipment LSNDS</li>  \
                            ",True)
            with st.container(border=True):
                st.error("Information Loss Test has potential schedule conflict with other tests", icon="❗")
                st.markdown("<li>Test Names: Path Confidence Test</li> \
                            <li>Scheduled Date and Time: September 2 12:00 - 13:00</li>  \
                            <li>Conflict Type: Has the same Equipment LSNDS</li>  \
                            ",True)
    
    with top_cols[1]:
        unscheduled = st.expander("⚠️ Three tests have not been scheduled on any Enviroment", expanded=True)

        with unscheduled:
            with st.container(border=True):
                st.warning("Adaptability Simulation 1 is not scheduled on any Site/Env", icon="⚠️")
                st.markdown("<li>Scheduled Date and Time: September 2 12:00 - 13:00</li>  \
                            <li>Test Equipment: LSNDS_PhysicsModel1</li> \
                            <li>Conflict Type: No Environment</li>  \
                            ",True)
            with st.container(border=True):
                st.warning("Adaptability Simulation 2 is not scheduled on any Site/Env", icon="⚠️")
                st.markdown("<li>Scheduled Date and Time: September 4 12:00 - 13:00</li>  \
                            <li>Test Equipment: LSNDS_PhysicsModel2</li> \
                            <li>Conflict Type: No Environment</li>  \
                            ",True)
            with st.container(border=True):
                st.warning("Electrical Simulation is not scheduled on any Site/Env", icon="⚠️")
                st.markdown("<li>Scheduled Date and Time: September 5 12:00 - 13:00</li>  \
                            <li>Test Equipment: LSNDS_ElectricalModel1</li> \
                            <li>Conflict Type: No Environment</li>  \
                            ",True)
                

# Function to make a issues widget that can create a brief of issues on other pages
def issuesinfo(height, ):
    st.markdown("<h6>Issues</h6>", True)
    with st.container(border=True, height=height):
        st.warning('Four tests have overlapped scheduling (find more info on Issues tab)', icon="⚠️")

        st.error("Electrical Test has potential schedule conflict with other tests", icon="❗")
        st.error("Path Accuracy Test has potential schedule conflict with other tests", icon="❗")

        st.error("Maneuverability Test has potential schedule conflict with other tests", icon="❗")
        st.error("Pathway Creation Time Test has potential schedule conflict with other tests", icon="❗")