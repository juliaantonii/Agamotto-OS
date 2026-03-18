import cv2
import numpy as np
import time
from vision import AgamottoEye
from forge_wireframe import AgamottoForgeWireframe

def start_agamotto():
    eye = AgamottoEye()
    forge = None 
    last_angles = [0, 0] # Histórico para suavização (Mão 0 e Mão 1)

    try:
        while True:
            frame = eye.get_frame()
            if frame is None: break
            h, w, _ = frame.shape
            
            if forge is None:
                forge = AgamottoForgeWireframe(w, h, cube_size=120)

            # --- LÓGICA PARA MÚLTIPLAS MÃOS ---
            if eye.last_result and eye.last_result.hand_landmarks:
                for idx, landmarks in enumerate(eye.last_result.hand_landmarks):
                    
                    # 1. IDENTIFICAÇÃO DA MÃO (L ou R)
                    hand_label = eye.last_result.handedness[idx][0].category_name
                    
                    if hand_label == "Left":
                        cube_color = (255, 200, 0) # Azul/Ciano (Lain Aesthetic)
                    else:
                        cube_color = (0, 255, 0)   # Verde (Agamotto Standard)

                    # 2. PONTOS DE REFERÊNCIA (Polegar e Indicador)
                    t_tip = landmarks[4]
                    i_tip = landmarks[8]

                    # 3. CÁLCULO DA POSIÇÃO COM OFFSET
                    real_center_x = (t_tip.x + i_tip.x) / 2
                    real_center_y = (t_tip.y + i_tip.y) / 2
                    
                    offset_y = 0.18 # Distância do cubo acima dos dedos
                    render_x = int(real_center_x * w)
                    render_y = int((real_center_y - offset_y) * h)

                    # 4. TAMANHO DINÂMICO (Pinch Zoom)
                    dist = np.sqrt((i_tip.x - t_tip.x)**2 + (i_tip.y - t_tip.y)**2)
                    new_size = int(dist * 850) 
                    new_size = np.clip(new_size, 40, 300)

                    # 5. ROTAÇÃO COM SUAVIZAÇÃO
                    dx = i_tip.x - t_tip.x
                    dy = i_tip.y - t_tip.y
                    target_angle = -np.degrees(np.arctan2(dy, dx))
                    
                    # Usa o idx (0 ou 1) para pegar o ângulo anterior da mão correta
                    current_angle = (last_angles[idx] * 0.8) + (target_angle * 0.2)
                    last_angles[idx] = current_angle

                    # --- EXECUÇÃO DO DESENHO ---
                    # Linha guia e ponto médio
                    finger_mid = (int(real_center_x * w), int(real_center_y * h))
                    cv2.line(frame, finger_mid, (render_x, render_y), cube_color, 1, cv2.LINE_AA)

                    # Atualiza vértices e desenha o cubo com a cor da mão
                    forge.update_vertices(new_size)
                    forge.project_and_draw(frame, render_x, render_y, current_angle, 0, color=cube_color)
                    
                    # Label flutuante
                    cv2.putText(frame, hand_label, (render_x - 20, render_y + 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # HUD de Status
            cv2.putText(frame, "AGAMOTTO-OS: MULTI-HAND ACTIVE", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Agamotto Eye - Multitouch", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        print("Encerrando Agamotto-OS...")
        eye.stop()

if __name__ == "__main__":
    start_agamotto()