import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class AgamottoEye:
    def __init__(self, model_path='src/hand_landmarker.task'):
        # 1. Configuração da Câmera (0 para Iriun conforme seu teste anterior)
        self.cap = cv2.VideoCapture(0) 
        
        # 2. Configurando o Detector de Mãos
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # 3. Variáveis de controle
        self.frame_count = 0
        self.last_result = None

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        
        # --- CORREÇÃO DA ORIENTAÇÃO ---
        # 1. Flip Horizontal (1): Para agir como um espelho
        frame = cv2.flip(frame, 0)
        
        # 2. Flip Vertical (0): Para você deixar de ficar de ponta-cabeça no Panda3D
        frame = cv2.flip(frame, 0)
        
        h, w, _ = frame.shape
        
        # Converter para o formato MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Timestamp crescente para evitar o ValueError
        timestamp_ms = self.frame_count * 33
        self.frame_count += 1
        
        # Detectar as mãos
        result = self.detector.detect_for_video(mp_image, timestamp_ms)
        self.last_result = result # Essencial para o forge.py ler os pontos

        # --- DESENHO DO ESQUELETO ---
        CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4), # Polegar
            (0, 5), (5, 6), (6, 7), (7, 8), # Indicador
            (0, 9), (9, 10), (10, 11), (11, 12), # Médio
            (0, 13), (13, 14), (14, 15), (15, 16), # Anelar
            (0, 17), (17, 18), (18, 19), (19, 20), # Mínimo
            (5, 9), (9, 13), (13, 17) # Palma
        ]

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                # Desenhar Linhas
                for start_idx, end_idx in CONNECTIONS:
                    start = hand_landmarks[start_idx]
                    end = hand_landmarks[end_idx]
                    # Nota: Como demos o flip vertical no frame, os pontos 
                    # do MediaPipe já estarão alinhados com a imagem desvirada.
                    pt1 = (int(start.x * w), int(start.y * h))
                    pt2 = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, pt1, pt2, (255, 255, 255), 1)

                # Desenhar Pontos
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1) 
        
        return frame

    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()