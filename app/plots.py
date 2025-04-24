import streamlit as st
from streamlit_extras.chart_container import chart_container
import pandas as pd
import altair as alt
from typing import List, Optional, Tuple

def plot_traffic_data(df:pd.DataFrame, selected_columns:Optional[List[str]]=None):
    
    if selected_columns is None:
        total_columns = [col for col in df.columns if col.endswith('_total')]
        instant_columns = [col for col in df.columns if col != 'time' and not col.endswith('_total')]
    
    else:
        total_columns = [col for col in selected_columns if col.endswith('_total')]
        instant_columns = [col for col in selected_columns if col != 'time' and not col.endswith('_total')]
    
    with chart_container(df):
        base = alt.Chart(df).encode(x=alt.X('time:Q', title='Tempo (segundos)'))
        
        area_charts = []
        for i, col in enumerate(total_columns):
            color = alt.Color(
                f"color:N", 
                scale=alt.Scale(domain=[col], range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][i:i+1]),
                legend=alt.Legend(title="Variáveis")
            )
            
            area = base.mark_area(opacity=0.5).encode(
                y=alt.Y(f"{col}:Q"),
                color=color
            ).transform_calculate(color=f"'{col}'")
            
            area_charts.append(area)
        
        bar_charts = []
        for i, col in enumerate(instant_columns):
            color = alt.Color(
                f"color:N", 
                scale=alt.Scale(domain=[col], range=['#9467bd', '#8c564b', '#e377c2', '#7f7f7f'][i:i+1]),
                legend=alt.Legend(title="Variáveis")
            )
            
            bar = base.mark_bar().encode(
                y=alt.Y(f"{col}:Q"),
                color=color
            ).transform_calculate(color=f"'{col}'")
            
            bar_charts.append(bar)
        
        charts = area_charts + bar_charts
        
        if charts:
            combined_chart = alt.layer(*charts).resolve_scale(
                y='independent'
            ).properties(
                width=700,
                height=400,
                title='Dados de Tráfego ao Longo do Tempo'
            ).interactive()
            
            st.altair_chart(combined_chart, use_container_width=True)
            
            return combined_chart
        else:
            st.warning("Nenhuma coluna selecionada para visualização")
            return None