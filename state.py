import streamlit as st

class State(object):
    role: str = None
    
    def __new__(cls):
        if not hasattr(cls,'instance'):
            cls.instance = super(State, cls).__new__(cls)

        return cls.instance

st.session_state.data = State()