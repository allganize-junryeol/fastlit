import streamlit as st

import streamlit as st
import streamlit.components.v1 as components
from frontend.file import js
from frontend.state import State

def main_desktop():
    st.set_page_config(
        layout="wide",
    )
    
    state = State()
    
    if not state.is_connected:
        with st.form("my_form"):
            st.write("Inside the form")
            state.username = st.text_input('Enter your username')
            state.password = st.text_input('Enter your password', type='password')
            state.entry_point_ip = st.text_input('Enter entry point IP')
            state.entry_point_port = st.text_input('Enter entry point port')
            
            if st.form_submit_button('Connect'):
                state.is_connected = True
    else:
        if st.button('Disconnect'):
            state.is_connected = False
            
        html = f"""
            <canvas id="desktop" style="width: 100%; height: 100%;"></canvas>
            {js("static/mstsc.js")}
            {js("static/keyboard.js")}
            {js("static/rle.js")}
            {js("static/canvas.js")}
            {js("static/rdp.js")}
        """
            
        components.html(html, height=500)


if __name__ == "__main__":
    main_desktop()