import streamlit as st
import altair as alt
import pandas as pd

def donut_chart_component():
    df = pd.DataFrame({"category": [1, 2, 3, 4, 5, 6], "value": [4, 6, 10, 3, 7, 8]})

    chart = alt.Chart(df).mark_arc(innerRadius=70).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal"),
    )
    
    st.altair_chart(chart, use_container_width=True)