import streamlit as st
from lib.car_counter import CarCounter
from lib import utils
import os
import uuid
from app.utils import redirect
import json
from lib.utils import infos

video_path = None

#FIXME: Redirect to results page after processing
redirect()

def free_video_file():
    if video_path is not None:
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Error deleting temporary file: {e}")

st.title("Novo Processamento de Video 📹")

cc = CarCounter(model_path='yolov8n.pt', verbose=1, streamlit=True)

video_file = st.file_uploader("Escolha um arquivo de vídeo", type=["mp4"], on_change=free_video_file)

if video_file is not None:
    process_id = str(uuid.uuid4())
    
    video_path = f".temp/{process_id}.mp4"
    
    with open(video_path, "wb") as f:
        f.write(video_file.read())
    
    image = utils.select_random_frame(video_path)
    
    main_cols = st.columns(2)
    
    with main_cols[1]:
        video_name = st.text_input("Nome do Vídeo", value=video_file.name, max_chars=50)
        
        sett_cols = st.columns(3)
        
        # Points
        sett_cols[0].info("Selecione dois pontos na imagem para definir a linha para delimitar o semáforo. ")
        x1 = sett_cols[0].slider("Ponto 1 X", min_value=0.0, max_value=1.0, value=0.20)
        y1 = sett_cols[0].slider("Ponto 1 Y", min_value=0.0, max_value=1.0, value=0.55)
        x2 = sett_cols[0].slider("Ponto 2 X", min_value=0.0, max_value=1.0, value=1.00)
        y2 = sett_cols[0].slider("Ponto 2 Y", min_value=0.0, max_value=1.0, value=0.55)
        
        points = ((x1, y1), (x2, y2))
        
        # Tracker Config
        conf = sett_cols[1].slider("Confiança", min_value=0.0, max_value=1.0, value=0.25, help=infos["conf"])
        iou  = sett_cols[1].slider("IOU", min_value=0.0, max_value=1.0, value=0.45, help=infos["iou"])
        tracker_model = sett_cols[1].selectbox("Modelo de Tracker", ["botsort", "bytetrack"], index=0, help=infos["tracker_model"])
        
        # Extra
        sett_cols[2].info("Defina o intervalo de tempo em segundos para o sinal verde e vermelho.")
        green_duration = sett_cols[2].slider("Duração Sinal Verde", min_value=0, max_value=40, value=20)
        red_duration   = sett_cols[2].slider("Duração Sinal Vermelho", min_value=0, max_value=40, value=5)
        process_btn = sett_cols[2].button("Processar Video", type="primary")
        
        if process_btn:
            process_id = f"{str(len(os.listdir(".videos")) + 1).zfill(2)} {video_name}"
            
            os.makedirs(f".videos/{process_id}", exist_ok=True)
            with st.spinner("Processando..."):
                output = f".videos/{process_id}/video.mp4"
                df, stats, video_out = cc.process(
                    video_path,
                    points,
                    output=output,
                    conf=conf,
                    iou=iou,
                    tracker_model=tracker_model, # type:ignore
                    green_duration=green_duration,
                    red_duration=red_duration
                )
                df.to_csv(f".videos/{process_id}/detections.csv", index=False)
                stats.to_csv(f".videos/{process_id}/stats.csv", index=False)
                
                with open(f".videos/{process_id}/config.json", "w") as f:
                    json.dump({
                        "points": points,
                        "conf": conf,
                        "iou": iou,
                        "tracker_model": tracker_model,
                        "green_duration": green_duration,
                        "red_duration": red_duration
                    }, f, indent=4)
                
                st.success("Processamento concluído!")
                st.balloons()
                st.session_state["redirect"] = process_id
                st.rerun()
                        
    with main_cols[0]:
        st.image(utils.plot_line_image(image,points), caption="Frame Selecionado", use_container_width=False)