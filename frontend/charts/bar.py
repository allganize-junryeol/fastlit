import streamlit as st
import plotly.graph_objs as go

def bar_chart_component():
    # Sample data
    categories = ['Category A', 'Category B', 'Category C']
    values = [10, 23, 15]

    # Create a bar chart
    bar_chart = go.Figure(data=[
        go.Bar(name='Values', x=categories, y=values)
    ])

    # Customize the layout
    bar_chart.update_layout(
        title='Sample Bar Chart',
        xaxis_title='Categories',
        yaxis_title='Values',
        template='plotly_dark'  # Optional: Change the theme to 'plotly_dark'
    )

    # Display the chart in Streamlit
    st.plotly_chart(bar_chart)