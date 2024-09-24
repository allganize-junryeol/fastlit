import random

import streamlit as st
import pandas as pd
import numpy as np

from frontend.charts.bar import bar_chart_component
from frontend.charts.donut import donut_chart_component

def main_dashboard():
    st.set_page_config(
        layout="wide",
    )

    st.header("Dashboard")
    
    dashboard_tab, list_tab = st.tabs(["Dashboard", "List"])

    with dashboard_tab:
        data = {
            "number_of_system": random.randint(5,10),
            "number_of_hardware": random.randint(5,10),
            "number_of_software": random.randint(5,10),
            "Updated_last_month": random.randint(5,10),
        }
                
        st.markdown(
            f"""
            | Number of System | Number of Hardware | Number of Software | Updated Last Month |
            |------------------|--------------------|--------------------|--------------------|
            | {data['number_of_system']} | {data['number_of_hardware']} | {data['number_of_software']} | {data['Updated_last_month']} |
            """
        )
        
        col1, col2 = st.columns([1, 3])

        with col1:
            donut_chart_component()
                
        with col2:
            bar_chart_component()

        df = pd.DataFrame(
            np.random.randn(10, 5), columns=("col %d" % i for i in range(5))
        )
        st.table(df)
        
        df = pd.DataFrame(
            np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
            columns=["lat", "lon"],
        )
        st.map(df)

    with list_tab:
        df = pd.DataFrame(
            np.random.randn(10, 5), columns=("col %d" % i for i in range(5))
        )
        st.table(df)


if __name__ == "__main__":
    main_dashboard()