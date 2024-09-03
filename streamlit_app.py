import streamlit as st

from auth import get_role, login_component, logout_component
from navigation import navigate


def home_page():
    st.header("Home")
    if get_role() is None:
        st.write("You are not logged in.")
        login_component()
    else:
        st.write("You are logged in.")
        logout_component()

if __name__ == "__main__":
    st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

    navigate(home_page)
