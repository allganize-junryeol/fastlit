import os
import streamlit as st

from auth import get_role

def main_admin_1():
    st.header("Admin 1")
    st.write(f"You are logged in as {get_role()}.")
    
if __name__ == "__main__":
    main_admin_1()