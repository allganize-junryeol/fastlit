import os
import streamlit as st

from auth import get_role

st.header("Dashboard")
st.write(f"You are logged in as {get_role()}.")
