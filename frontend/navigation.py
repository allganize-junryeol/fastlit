from typing import Callable

import streamlit as st

from frontend.auth import Role, get_role

from frontend.pages.admin.admin_1 import main_admin_1
from frontend.pages.admin.admin_2 import main_admin_2
from frontend.pages.dashboard.dashboard import main_dashboard
from frontend.pages.dashboard.desktop import main_desktop
from frontend.pages.dashboard.terminal import main_terminal
from frontend.pages.dashboard.topology import main_topology

def navigate(main_home: Callable):    
    role = get_role()
    
    page_dict = {}

    if role is None:
        page_dict[""] =  [
            st.Page(main_home, title="Home", icon=":material/home:"),
        ]
    
    if role is not None:
        page_dict[""] = [
            st.Page(main_home, title="Home", icon=":material/home:"),
        ]
        page_dict["Dashboard"] = [
            st.Page(main_dashboard, title="Dashboard", icon=":material/dashboard:", url_path="dashboard"),
            st.Page(main_topology, title="Topology", icon=":material/hub:", url_path="topology"),
            st.Page(main_terminal, title="Terminal", icon=":material/terminal:", url_path="terminal"),
            st.Page(main_desktop, title="Desktop", icon=":material/monitor:", url_path="desktop"),
        ]

    if role in [Role.ADMIN]:
        page_dict["Admin"] = [
            st.Page(main_admin_1, title="Admin 1", icon=":material/admin_panel_settings:", url_path="admin_1"),
            st.Page(main_admin_2, title="Admin 2", icon=":material/admin_panel_settings:", url_path="admin_2"),
        ]
    
    return st.navigation(page_dict).run()
