import streamlit as st
from streamlit_ttyd import terminal
import time 

import streamlit as st
import streamlit.components.v1 as components
from frontend.file import css, js
from frontend.state import State

def main_terminal():
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
                print("Connecting ...")
                state.is_connected = True
    else:
        if st.button('Disconnect'):
            state.is_connected = False
            
        html = f"""
            <div id="terminal"></div>
            {css("static/xterm.min.css")}
            {js("static/xterm.min.js")}
            {js("static/xterm-addon-fit.min.js")}
            {js("static/ssh.js")}
        """
            
        components.html(html, height=600)


if __name__ == "__main__":
    main_terminal()