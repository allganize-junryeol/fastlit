import streamlit as st
import pandas as pd
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.layouts import ForceLayout, StressLayout

def main_topology():
    st.set_page_config(
        layout="wide",
    )

    # 1. CSV 파일 읽기
    df = pd.read_csv('data/ship_systems_edge.csv')

    # 3. 노드 및 엣지를 저장할 리스트 생성
    nodes = {}
    edges = []

    # 4. 소스, 목적지 노드를 생성하고 연결
    for index, row in df.iterrows():
        source = row['source']
        destination = row['destination']
        direction = row['direction']
        
        # 5. 노드 위치 및 중복 확인 (중복 없이 추가)
        if source not in nodes:
            nodes[source] = StreamlitFlowNode(source, (0,0), {'content': source})
        if destination not in nodes:
            nodes[destination] = StreamlitFlowNode(destination, (0,0), {'content': destination})
            
        if direction == 'single':
            edges.append(StreamlitFlowEdge(f'{source}-{destination}', source, destination))
        elif direction == 'dual':
            edges.append(StreamlitFlowEdge(f'{source}-{destination}', source, destination))
            edges.append(StreamlitFlowEdge(f'{destination}-{source}', destination, source))

    streamlit_flow('network_connections', list(nodes.values()), edges, layout=StressLayout(), fit_view=True)

if __name__ == "__main__":
    main_topology()