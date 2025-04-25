import streamlit as st
import pandas as pd
import altair as alt
from typing import List
from lib.utils import infos

color_mapping = {
    'detected': '#1f77b4',
    'detected_total': '#1f77b4',
    'green': '#2ca02c',
    'green_total': '#2ca02c',
    'red': '#d62728', 
    'red_total': '#d62728',
    'passed': '#ffbb00',
    'passed_total': '#ffbb00'
}

order_mapping = {
    'detected': 3,  
    'detected_total': 3,
    'passed': 2,
    'passed_total': 2,
    'green': 1,
    'green_total': 1,
    'red': 0,
    'red_total': 0
}

def plot_traffic_data_total(df: pd.DataFrame, total_columns: List[str]):
    if not total_columns:
        st.warning("Nenhuma coluna de totais selecionada para visualização")
        
    total_columns_ordered = sorted(total_columns, key=lambda x: order_mapping[x], reverse=True)
    
    charts = []
    for col in total_columns_ordered:
        chart = alt.Chart(df).mark_area(
            opacity=0.6,
            line=True
        ).encode(
            x=alt.X('time:Q', title='Tempo (segundos)'),
            y=alt.Y(f'{col}:Q', title='Ao longo do tempo'),
            color=alt.value(color_mapping[col])
        )
        charts.append(chart)
    
    area_chart = alt.layer(*charts).properties(
        width=700,
        height=400,
        title='Dados de Tráfego Acumulados'
    ).interactive()
    
    legend_data = pd.DataFrame({
        'variável': total_columns_ordered,
        'valor': [1] * len(total_columns_ordered)
    })
    
    legend = alt.Chart(legend_data).mark_point().encode(
        y=alt.Y('valor:Q', axis=None),
        color=alt.Color('variável:N', 
                      scale=alt.Scale(domain=total_columns_ordered, 
                                     range=[color_mapping[col] for col in total_columns_ordered]),
                      legend=alt.Legend(title="Variáveis (totais)")
                     )
    )
    
    combined_chart = alt.layer(area_chart, legend)
    
    st.altair_chart(combined_chart, use_container_width=True)      

def plot_traffic_data_total_instant(df: pd.DataFrame, instant_columns: List[str]):
    if not instant_columns:
        st.warning("Nenhuma coluna instantânea selecionada para visualização")
        return
    instant_columns_ordered = sorted(instant_columns, key=lambda x: order_mapping[x], reverse=True)
    
    charts = []
    for col in instant_columns_ordered:
        chart = alt.Chart(df).mark_bar(
            opacity=0.8
        ).encode(
            x=alt.X('time:Q', title='Tempo (segundos)'),
            y=alt.Y(f'{col}:Q', title='Por segundo'),
            color=alt.value(color_mapping[col])
        )
        charts.append(chart)
    
    bar_chart = alt.layer(*charts).properties(
        width=700,
        height=400,
        title='Dados de Tráfego por Segundo'
    ).interactive()
    
    legend_data = pd.DataFrame({
        'variável': instant_columns_ordered,
        'valor': [1] * len(instant_columns_ordered)
    })
    
    legend = alt.Chart(legend_data).mark_point().encode(
        y=alt.Y('valor:Q', axis=None),
        color=alt.Color('variável:N', 
                      scale=alt.Scale(domain=instant_columns_ordered, 
                                     range=[color_mapping[col] for col in instant_columns_ordered]),
                      legend=alt.Legend(title="Variáveis (por segundo)")
                     )
    )
    
    combined_bar_chart = alt.layer(bar_chart, legend)
    
    st.altair_chart(combined_bar_chart, use_container_width=True)
        
    

def show_metrics(df:pd.DataFrame, config:dict):
    st.subheader("Métricas Gerais e Configuração") 
    
    metrics = {
        'Total Detectados': df['detected_total'].max(),
        'Total Sinal Verde': df['green_total'].max(),
        'Total Sinal Vermelho': df['red_total'].max(),
        'Confiança': config['conf'],
        'IOU': config['iou'],
        'Modelo de Tracker': config['tracker_model'],
    }
    
    cols = st.columns(len(metrics))
    
    for i, (metric, value) in enumerate(metrics.items()):
        helper = infos.get(metric.lower()[:4]) if metric != 'Modelo de Tracker' else infos.get(value.lower())
        cols[i].metric(label=metric, value=value, border=True, help=helper)