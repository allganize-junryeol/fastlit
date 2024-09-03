from typing import Callable

import streamlit as st

from auth import Role, get_role

def navigate(home_page: Callable):
    
    role = get_role()
    
    page_dict = {}

    if role is None:
        page_dict[""] =  [
            st.Page(home_page, title="Home", icon=":material/home:"),
        ]
    
    if role is not None:
        page_dict[""] = [
            st.Page(home_page, title="Home", icon=":material/home:"),
        ]
        page_dict["Dashboard"] = [
            st.Page("pages/dashboard/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
        ]

    if role in [Role.ADMIN]:
        page_dict["Admin"] = [
            st.Page("pages/admin/admin_1.py", title="Admin 1", icon=":material/admin_panel_settings:"),
            st.Page("pages/admin/admin_2.py", title="Admin 2", icon=":material/admin_panel_settings:"),
        ]
    
    return st.navigation(page_dict).run()
