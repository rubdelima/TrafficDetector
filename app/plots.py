import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Optional
from lib.utils import infos

def plot_traffic_data(df: pd.DataFrame, selected_columns: Optional[List[str]] = None):
    
    if selected_columns is None:
        total_columns = [col for col in df.columns if col.endswith('_total')]
        instant_columns = [col for col in df.columns if col != 'time' and not col.endswith('_total')]
    else:
        total_columns = [col for col in selected_columns if col.endswith('_total')]
        instant_columns = [col for col in selected_columns if col != 'time' and not col.endswith('_total')]
    
    # Definir cores específicas para cada tipo de dado
    color_mapping = {
        'detected': '#1f77b4',  # azul
        'detected_total': '#1f77b4',
        'green': '#2ca02c',  # verde
        'green_total': '#2ca02c',
        'red': '#d62728',  # vermelho
        'red_total': '#d62728',
        'passed': '#ffbb00',  # amarelo
        'passed_total': '#ffbb00'
    }
    
    # Criar gráficos de área para totais
    if total_columns:
        # Preparar dados para gráfico de área
        area_data = df[['time'] + total_columns].melt(
            id_vars=['time'], 
            value_vars=total_columns,
            var_name='variável', 
            value_name='total'
        )
        
        area_chart = alt.Chart(area_data).mark_area(opacity=0.6).encode(
            x=alt.X('time:Q', title='Tempo (segundos)'),
            y=alt.Y('total:Q', title='Ao longo do tempo'),
            color=alt.Color('variável:N', 
                          scale=alt.Scale(domain=list(total_columns), 
                                         range=[color_mapping[col] for col in total_columns]),
                          legend=alt.Legend(title="Variáveis (totais)")
                         )
        ).properties(
            width=700,
            height=400
        )
    else:
        area_chart = None
    
    # Criar gráficos de barras para valores instantâneos
    if instant_columns:
        # Preparar dados para gráfico de barras
        bar_data = df[['time'] + instant_columns].melt(
            id_vars=['time'], 
            value_vars=instant_columns,
            var_name='variável', 
            value_name='valor'
        )
        
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X('time:Q', title='Tempo (segundos)'),
            y=alt.Y('valor:Q', title='Por segundo'),
            color=alt.Color('variável:N', 
                          scale=alt.Scale(domain=list(instant_columns), 
                                         range=[color_mapping[col] for col in instant_columns]),
                          legend=alt.Legend(title="Variáveis (por segundo)")
                         )
        ).properties(
            width=700,
            height=400
        )
    else:
        bar_chart = None
    
    # Combinar os gráficos
    if area_chart and bar_chart:
        combined_chart = alt.layer(area_chart, bar_chart).resolve_scale(
            y='independent'
        ).properties(
            title='Dados de Tráfego ao Longo do Tempo'
        ).interactive()
        
        st.altair_chart(combined_chart, use_container_width=True)
        return combined_chart
    
    elif area_chart:
        st.altair_chart(area_chart, use_container_width=True)
        return area_chart
    
    elif bar_chart:
        st.altair_chart(bar_chart, use_container_width=True)
        return bar_chart
    
    else:
        st.warning("Nenhuma coluna selecionada para visualização")
        return None

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