import streamlit as st
import pandas as pd # type:ignore
from app.utils import get_column_ratios, dowload_container
from app.plots import plot_traffic_data_total, plot_traffic_data_total_instant, show_metrics
import json

total_columns = ['detected_total', 'green_total', 'red_total', 'passed_total']
instant_columns = ['detected', 'green', 'red', 'passed']

def show_results(video_id, path="videos"):
    
    result_path = f".{path}/{video_id}"
    
    st.title("Resultados")
    
    df_stats = pd.read_csv(f"{result_path}/stats.csv")
    
    cols = st.columns(get_column_ratios(f"{result_path}/video.mp4"))
    
    with cols[0]:
        st.video(f"{result_path}/video.mp4")
    
    with cols[1]:
        with open(f"{result_path}/config.json", "r") as f:
            config = json.load(f)
        show_metrics(df_stats, config)
        
        tab1, tab2 = st.tabs(["Valores Totais", "Valores por Segundo"])
        
        with tab1:
            selected_total = st.multiselect(
                "Colunas Totais Para Visualização", total_columns, default=total_columns)
            plot_traffic_data_total(df_stats, selected_total)
        
        with tab2:
            selected_instant = st.multiselect(
                "Colunas Instantâneas Para Visualização", instant_columns, default=instant_columns)
            plot_traffic_data_total_instant(df_stats, selected_instant)
            
    with cols[2]:
        dowload_container(result_path, hortizontal=False)
        
        