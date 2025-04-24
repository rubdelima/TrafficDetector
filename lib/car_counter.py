import cv2
import numpy as np
import pandas as pd # type:ignore
from typing import Tuple, Union, List, Dict, Literal
from ultralytics import YOLO # type:ignore
from tqdm.auto import tqdm # type:ignore
import torch
from stqdm import stqdm

class CarCounter:
    def __init__(self, model_path: str = 'yolov8n.pt', verbose: int = 0, streamlit: bool = False):
        """
        model_path: caminho para pesos YOLOv8
        verbose: nível de log (0 silencia, ≥1 mostra)
        """
        self.device  = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.fp16    = (self.device != 'cpu')
        self.model   = YOLO(model_path)
        self.verbose = verbose
        self.tqdm    = stqdm if streamlit else tqdm

    def _log(self, msg: str, level: int = 1):
        if self.verbose >= level:
            tqdm.write(msg)

    def _open_video(self, path: str) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {path}")
        return cap

    def _init_writer(self, output: str, fps: float, size: Tuple[int,int]) -> cv2.VideoWriter:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type:ignore
        return cv2.VideoWriter(output, fourcc, fps, size)

    def _compute_line(self, points: Tuple[Tuple[float,float],Tuple[float,float]],
                      W: int, H: int) -> Tuple[Tuple[int,int],Tuple[int,int]]:
        def to_px(pt):
            x,y = pt
            return (int(x*W) if 0<=x<=1 else int(x),
                    int(y*H) if 0<=y<=1 else int(y))
        return to_px(points[0]), to_px(points[1])

    def _process_frame(
        self,
        result,
        idx: int,
        fps: float,
        p1: Tuple[int,int],
        p2: Tuple[int,int],
        cycle: int,
        green_dur: int,
        pass_state: Dict[int,int]
    ) -> Tuple[List[Dict], np.ndarray, int, int]:
        """
        Processa um único frame:
          - result: saída do model.track()
          - idx, fps: para time
          - p1, p2: linha de contagem
          - cycle, green_dur, red_dur: semáforo
          - pass_state: dict[id] -> -1/0/1
        Retorna:
          det_recs: lista de registros deste frame,
          annotated: frame anotado,
          inc_green, inc_red: incrementos de contagem
        """
        frame = result.orig_img
        ts    = idx / fps

        # semáforo
        light = 'green' if (int(ts) % cycle) < green_dur else 'red'
        line_color = (0,255,0) if light=='green' else (0,0,255)

        annotated = frame.copy()
        cv2.line(annotated, p1, p2, line_color, 2)

        # extração
        boxes = result.boxes.xyxy.cpu().numpy()
        ids   = result.boxes.id.cpu().numpy().astype(int)
        cls   = result.boxes.cls.cpu().numpy().astype(int)
        mask  = np.isin(cls, [2,3,5,7])
        boxes = boxes[mask]
        ids   = ids[mask]

        inc_g = inc_r = 0
        det_recs: List[Dict] = []

        for (x1,y1,x2,y2), tid in zip(boxes, ids):
            cx, cy = int((x1+x2)/2), int((y1+y2)/2)
            pass_state.setdefault(tid, 0)

            # distância à linha
            dist = abs((p2[1]-p1[1])*cx - (p2[0]-p1[0])*cy +
                       p2[0]*p1[1] - p2[1]*p1[0]) \
                   / np.hypot(p2[1]-p1[1], p2[0]-p1[0])

            if dist < 5 and pass_state[tid] == 0:
                if light == 'green':
                    pass_state[tid] = 1
                    inc_g += 1
                else:
                    pass_state[tid] = -1
                    inc_r += 1

            det_recs.append({
                'time': ts,
                'id': tid,
                'x1': cx,
                'y1': cy,
                'pass': pass_state[tid]
            })

            color = {0:(0,0,0), 1:(0,255,0), -1:(0,0,255)}[pass_state[tid]]
            x1i,y1i,x2i,y2i = map(int, (x1,y1,x2,y2))
            cv2.rectangle(annotated, (x1i,y1i), (x2i,y2i), color, 2)
            cv2.putText(annotated, f"ID{tid}", (x1i, y1i-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return det_recs, annotated, inc_g, inc_r

    @staticmethod
    def compute_stats_from_detections(df: pd.DataFrame) -> pd.DataFrame:
        """
        Reconstrói o DataFrame de estatísticas a partir do df de detecções por id do carro.
        """
        df = df.sort_values('time')
        times = df['time'].unique()
        first_appear = df.groupby('id')['time'].min()
        events = (
            df[df['pass'] != 0]
              .sort_values('time')
              .drop_duplicates('id', keep='first')[['time','pass']]
        )
        green_ct = events[events['pass']==1]['time'].value_counts()
        red_ct   = events[events['pass']==-1]['time'].value_counts()

        rows, cum_g, cum_r = [], 0, 0
        for t in times:
            det     = int((df['time']==t).sum())
            det_tot = int((first_appear <= t).sum())
            g       = int(green_ct.get(t,0))
            r       = int(red_ct.get(t,0))
            cum_g  += g
            cum_r  += r
            rows.append({
                'time': t,
                'detected': det,
                'detected_total': det_tot,
                'green': g,
                'green_total': cum_g,
                'red': r,
                'red_total': cum_r,
                'passed': g+r,
                'passed_total': cum_g+cum_r
            })
        return pd.DataFrame(rows)

    def process(
        self,
        video_path: str,
        points: Tuple[Tuple[float,float],Tuple[float,float]],
        output: str = 'output.mp4',
        conf: float = 0.25,
        iou: float = 0.45,
        tracker_model: Literal['botsort','bytetrack'] = 'botsort',
        green_duration: int = 20,
        red_duration: int = 5
    ) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
        """
        Executa detecção+tracking, salva vídeo anotado em `output`.

        Retorna:
          df: cada detecção ['time','id','x1','y1','pass']
          stats_df: via compute_stats_from_detections(df)
          output: caminho do arquivo MP4 gerado
        """
        cap    = self._open_video(video_path)
        fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
        W      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = self._init_writer(output, fps, (W,H))
        p1,p2  = self._compute_line(points, W, H)
        cycle  = green_duration + red_duration

        det_records: List[Dict] = []
        pass_state: Dict[int,int] = {}
        green_total = red_total = 0

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        
        # https://docs.ultralytics.com/pt/modes/track/#available-trackers
        stream = self.model.track(
            source=video_path,
            tracker=f'{tracker_model}.yaml',
            stream=True,
            device=self.device,
            half=self.fp16,
            conf=conf,
            iou=iou,
            verbose=(self.verbose>=2)
        )

        for idx, result in enumerate(self.tqdm(stream, total=total, desc="Processing", unit="frame")):
            dets, annotated, dg, dr = self._process_frame(
                result, idx, fps, p1, p2, cycle,
                green_duration, pass_state
            )
            
            det_records.extend(dets)
            green_total += dg
            red_total   += dr
            
            writer.write(annotated)

        cap.release()
        writer.release()

        df       = pd.DataFrame(det_records)
        stats_df = self.compute_stats_from_detections(df)
        return df, stats_df, output