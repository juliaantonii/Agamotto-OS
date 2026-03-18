import cv2
import numpy as np
import time
from vision import AgamottoEye
from forge_wireframe import AgamottoForgeWireframe

def start_agamotto():
    eye = AgamottoEye()
    forge = None 
    # Agora usamos um dicionário ou lista para guardar o histórico de cada mão
    last_angles = [0, 0] 

    try:
        while True:
            frame = eye.get_frame()
            if frame is None: break
            h, w, _ = frame.shape
            
            if forge is None:
                forge = AgamottoForgeWireframe(w, h, cube_size=120)

            # --- LÓGICA PARA MÚLTIPLAS MÃOS ---
            if eye.last_result and eye.last_result.hand_landmarks:
                
                # O enumerate nos dá o índice (0 ou 1) e os pontos daquela mão
                for idx, landmarks in enumerate(eye.last_result.hand_landmarks):
                    
                    # 1. REFERÊNCIAS
                    t_tip = landmarks[4]
                    i_tip = landmarks[8]

                    # 2. POSIÇÃO E OFFSET
                    real_center_x = (t_tip.x + i_tip.x) / 2
                    real_center_y = (t_tip.y + i_tip.y) / 2
                    render_x = int(real_center_x * w)
                    render_y = int((real_center_y - 0.18) * h)

                    # 3. TAMANHO
                    dist = np.sqrt((i_tip.x - t_tip.x)**2 + (i_tip.y - t_tip.y)**2)
                    new_size = int(dist * 850)
                    new_size = np.clip(new_size, 40, 250)

                    # 4. ROTAÇÃO SUAVIZADA POR MÃO
                    dx = i_tip.x - t_tip.x
                    dy = i_tip.y - t_tip.y
                    target_angle = -np.degrees(np.arctan2(dy, dx))
                    
                    # Usamos o índice (idx) para acessar o ângulo anterior daquela mão específica
                    current_angle = (last_angles[idx] * 0.8) + (target_angle * 0.2)
                    last_angles[idx] = current_angle

                    # --- DESENHO ---
                    forge.update_vertices(new_size)
                    forge.project_and_draw(frame, render_x, render_y, current_angle, 0)
                    
                    # Identificador visual (Mão 1 ou Mão 2)
                    cv2.putText(frame, f"H-{idx+1}", (render_x, render_y - 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Agamotto Eye - Multitouch", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        eye.stop()

if __name__ == "__main__":
    start_agamotto()