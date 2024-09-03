from enum import Enum

import streamlit as st

class Role(str, Enum):
    REQUESTER = "Requester"
    RESPONDER = "Responder"
    ADMIN = "Admin"

def get_role():
    return st.session_state.role if "role" in st.session_state else None

def login(role: Role):
    st.session_state.role = role
    st.rerun()

def logout():
    st.session_state.role = None
    st.rerun()

def login_component():
    role = st.selectbox("Choose your role", [role.value for role in Role])

    if st.button("Log in"):
        login(role)

def logout_component():
    if st.button("Log out"):
        logout()
