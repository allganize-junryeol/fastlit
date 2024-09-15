import streamlit.components.v1 as components


def js(file_path):
    with open(file_path, "r") as f:
        script = f'<script>{f.read()}</script>'
        return script

def css(file_path):
    with open(file_path, "r") as f:
        style = f'<style>{f.read()}</style>'
        return style
