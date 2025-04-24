import streamlit as st
from streamlit_extras.chart_container import chart_container
import pandas as pd
import altair as alt
from app.utils import get_column_ratios
from app.plots import plot_traffic_data

def show_results(video_id):
    
    st.title("Resultados")
    st.write(f"Aqui estão os resultados do processamento de vídeo {video_id}.")
    
    df_stats = pd.read_csv(f".videos/{video_id}/stats.csv")
    
    cols = st.columns(get_column_ratios(f".videos/{video_id}/video.mp4"))
    
    with cols[0]:
        st.video(f".videos/{video_id}/video.mp4")
    
    with cols[1]:
        cols_df = df_stats.columns.tolist()
        df_columns = st.multiselect("Colunas Para Visualização", cols_df, default=cols_df[2:])
        plot_traffic_data(df_stats, df_columns)