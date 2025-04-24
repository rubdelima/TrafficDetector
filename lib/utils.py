import cv2
import random
import numpy as np
from typing import Tuple

def select_random_frame(video: str) -> np.ndarray:
    """
    Abre o vídeo em `video_path` e retorna um frame aleatório (BGR).
    """
    cap = cv2.VideoCapture(video)
    
    if not cap.isOpened():
        cap.release()
        raise IOError(f"Não foi possível abrir o vídeo: {video}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    idx   = random.randint(0, total - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise ValueError(f"Não conseguiu ler o frame #{idx}")
    
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def plot_line_image(
    frame: np.ndarray,
    points: Tuple[Tuple[float, float], Tuple[float, float]]
) -> np.ndarray:
    """
    Desenha a linha definida por `points` em `frame` (BGR) e retorna o resultado em RGB.
    """
    h, w = frame.shape[:2]
    def to_px(pt):
        x, y = pt
        px = int(x * w) if 0 <= x <= 1 else int(x)
        py = int(y * h) if 0 <= y <= 1 else int(y)
        return px, py

    p1 = to_px(points[0])
    p2 = to_px(points[1])

    annotated = frame.copy()
    cv2.line(annotated, p1, p2, (0, 255, 0), 2)

    return annotated
