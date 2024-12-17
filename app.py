# Import streamlit to make frontend components
import streamlit as st

# Import functions from other files, where the View is created
from dashboard import dashschedule, dashresults, dashreqs
from architecture import sysarcfunc
from issues import sysissues
# from home import homefunc, progmgmtfunc
from orbit import orbitfunc

# Set page configuration, page title is the titlebar content, icon also appears on title bar
st.set_page_config(page_title="Dashboard", page_icon="🍩", layout="wide")

# main entrypoint of the application, gets called when the app runs
def main():

    # For the heading on the page
    st.header("🧮 Dashboard", divider="red")

    # create the list of tabs in a list
    TABS = ["Requirements", "Architecture", "Orbit",  "Test Strategy", "Warnings/Issues"]
    # pass the list to make a tab component
    tabs = st.tabs(TABS)

    # call each tab and call the function that containes the Page view under the tab section
    with tabs[0]:
        dashreqs()
    with tabs[1]:
        sysarcfunc()
    with tabs[2]:
        orbitfunc()
        pass
    with tabs[3]:
        dashschedule()
        dashresults()
    with tabs[4]:
        # issues/warnings tab view
        sysissues()


if __name__ == "__main__":
    main()