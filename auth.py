from enum import Enum

import streamlit as st

from state import State

class Role(str, Enum):
    REQUESTER = "Requester"
    RESPONDER = "Responder"
    ADMIN = "Admin"

def get_role():
    return State().role

def login(role: Role):
    State().role = role
    st.rerun()

def logout():
    State().role = None
    st.rerun()

def login_component():
    role = st.selectbox("Choose your role", [role.value for role in Role])

    if st.button("Log in"):
        login(role)

def logout_component():
    if st.button("Log out"):
        logout()
