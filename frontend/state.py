import streamlit as st

class State(object):
    role: str = None
    
    is_connected: bool = False
    username: str = ""
    password: str = ""
    entry_point_ip: str = ""
    entry_point_port: str = ""
    
    def __new__(cls):
        if not hasattr(cls,'instance'):
            cls.instance = super(State, cls).__new__(cls)

        return cls.instance

st.session_state.data = State()