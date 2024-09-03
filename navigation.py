import streamlit as st

from auth import Role, get_role, login_component, logout_component

def home_page():
    st.header("Home")
    if get_role() is None:
        st.write("You are not logged in.")
        login_component()
    else:
        st.write("You are logged in.")
        logout_component()

def navigate():
    
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
