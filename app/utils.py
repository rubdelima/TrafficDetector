# Em app/utils.py:
import streamlit as st
from typing import List, Tuple
import cv2

def redirect():
    try:
        if "redirect" not in st.session_state:
            st.session_state.redirect = None

        if st.session_state.redirect is not None:
            result_id = st.session_state.redirect
            st.session_state.redirect = None
            try:
                st.switch_page(f"result_{result_id}")
            except Exception as e:
                st.error(f"Erro ao redirecionar: {e}")
    except:
        st.success(f"Você pode ver os resultados do vídeo {result_id} na aba de resultados.")

def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Não foi possível abrir o vídeo: {video_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    cap.release()
    return width, height

def get_column_ratios(video_path: str) -> List[int]:

    width, height = get_video_dimensions(video_path)
    aspect_ratio = width / height
    
    if aspect_ratio < 0.8:
        return [2, 6, 1]
    
    return [2, 2, 1]
            
def dowload_container(result_path, hortizontal=True):
    downloads = [
        {"icon" : "📹" , "ext" : ".mp4",  "label" : "Download Video (mp4)", "path" : f"{result_path}/video.mp4"},
        {"icon" : "🔎" , "ext" : ".csv",  "label" : "Download Detecções (csv)", "path" : f"{result_path}/detections.csv"},
        {"icon" : "📊" , "ext" : ".csv",  "label" : "Download Estatísticas (csv)", "path" : f"{result_path}/stats.csv"},
        {"icon" : "⚙️" , "ext" : ".json", "label" : "Download Configuração (json)", "path" : f"{result_path}/config.json"},
    ]
    
    cols = st.columns(len(downloads) if hortizontal else 1)
    
    for i, download in enumerate(downloads):
        with cols[i if hortizontal else 0]:
            st.download_button(
                label=download["label"],
                data=open(download["path"], "rb"),
                file_name=download["label"].replace(" ", "_").lower() + download["ext"],
                mime="application/octet-stream",
                use_container_width=True,
                icon=download["icon"],
            )
    
    