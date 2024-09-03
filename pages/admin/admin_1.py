import streamlit as st

from auth import get_role

st.header("Admin 1")
st.write(f"You are logged in as {get_role()}.")
