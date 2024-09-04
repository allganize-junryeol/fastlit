import streamlit as st

from frontend.auth import get_role, login_component, logout_component
from frontend.navigation import navigate


def main_home():
    if get_role() is None:
        st.set_page_config(initial_sidebar_state="collapsed")
        st.html(
            """
            <style>
                [data-testid="stSidebar"] {
                    display: none
                }
                [data-testid="collapsedControl"] {
                    display: none
                }
            </style>
            """
        )
    else:
        st.set_page_config(initial_sidebar_state="expanded")

    st.header("Home")
    if get_role() is None:
        st.write("You are not logged in.")
        login_component()
    else:
        st.write("You are logged in.")
        logout_component()

if __name__ == "__main__":
       
    navigate(main_home)
    st.logo("frontend/images/horizontal_blue.png", icon_image="frontend/images/icon_blue.png")
