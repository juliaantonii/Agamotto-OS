import cv2
import numpy as np
from vision import AgamottoEye
from forge_wireframe import AgamottoForgeWireframe

def start_agamotto():
    eye = AgamottoEye()
    forge = None 
    last_angles = [0, 0] # [0] Esquerda, [1] Direita
    
    # --- VARIÁVEIS DE ESTADO (MÁQUINA DE ESTADOS) ---
    fusion_enabled = False  # Estado persistente da fusão
    can_toggle = True       # Trava para evitar múltiplos cliques acidentais
    
    FUSION_THRESHOLD = 60   # Distância para o "clique" dos indicadores
    FUSION_COLOR = (255, 0, 255) # Magenta/Neon para o Cubo Mestre

    try:
        while True:
            frame = eye.get_frame()
            if frame is None: break
            h, w, _ = frame.shape
            
            if forge is None:
                forge = AgamottoForgeWireframe(w, h, cube_size=120)

            # --- 1. COLETA E MAPEAMENTO DE DADOS ---
            if eye.last_result and eye.last_result.hand_landmarks:
                hand_data = {}
                for idx, landmarks in enumerate(eye.last_result.hand_landmarks):
                    label = eye.last_result.handedness[idx][0].category_name
                    
                    t_tip = landmarks[4]
                    i_tip = landmarks[8]
                    palm_center = landmarks[9]
                    
                    hand_data[label] = {
                        "index_tip": (int(i_tip.x * w), int(i_tip.y * h)),
                        "center": (int(palm_center.x * w), int(palm_center.y * h)),
                        "render_pos": (int(palm_center.x * w), int((palm_center.y - 0.2) * h)), 
                        "pinch": np.sqrt((i_tip.x - t_tip.x)**2 + (i_tip.y - t_tip.y)**2),
                        "angle": -np.degrees(np.arctan2(i_tip.y - t_tip.y, i_tip.x - t_tip.x))
                    }

                # --- 2. LÓGICA DE DISPARO (TOGGLE) ---
                if "Left" in hand_data and "Right" in hand_data:
                    # Verifica se ambas as mãos possuem a chave index_tip
                    if "index_tip" in hand_data["Left"] and "index_tip" in hand_data["Right"]:
                        p1 = np.array(hand_data["Left"]["index_tip"])
                        p2 = np.array(hand_data["Right"]["index_tip"])
                        
                        dist_hands = np.linalg.norm(p1 - p2)

                        # Se os dedos se tocam
                        if dist_hands < FUSION_THRESHOLD:
                            if can_toggle:
                                fusion_enabled = not fusion_enabled # Inverte o estado
                                can_toggle = False # Trava o clique
                        else:
                            can_toggle = True # Destrava quando os dedos se afastam

                # --- 3. RENDERIZAÇÃO CONDICIONAL ---
                if fusion_enabled and "Left" in hand_data and "Right" in hand_data:
                    # MODO FUSÃO ATIVO (Persistent)
                    # Usamos o centro da tela ou a posição média atual para o cubo central
                    mid_x = (hand_data["Left"]["center"][0] + hand_data["Right"]["center"][0]) // 2
                    mid_y = (hand_data["Left"]["center"][1] + hand_data["Right"]["center"][1]) // 2
                    
                    # Controle Colaborativo:
                    # Direita define o tamanho (Pinch)
                    fusion_size = int(hand_data["Right"]["pinch"] * 900)
                    fusion_size = np.clip(fusion_size, 50, 450)
                    
                    # Esquerda define a rotação
                    curr_angle = (last_angles[0] * 0.7) + (hand_data["Left"]["angle"] * 0.3)
                    last_angles[0] = curr_angle

                    # Desenho do Cubo de Fusão
                    forge.update_vertices(fusion_size)
                    forge.project_and_draw(frame, mid_x, mid_y, curr_angle, 0, color=FUSION_COLOR)
                    
                    # Feedback de Conexão
                    cv2.line(frame, hand_data["Left"]["index_tip"], hand_data["Right"]["index_tip"], (255, 255, 255), 1)
                    cv2.putText(frame, "HYPER-FUSION LOCKED", (mid_x - 100, mid_y - 130), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, FUSION_COLOR, 2)

                else:
                    # MODO INDEPENDENTE (Cubos L/R)
                    for label, data in hand_data.items():
                        color = (255, 200, 0) if label == "Left" else (0, 255, 0)
                        
                        size = int(data["pinch"] * 850)
                        size = np.clip(size, 40, 300)
                        
                        idx = 0 if label == "Left" else 1
                        curr_angle = (last_angles[idx] * 0.8) + (data["angle"] * 0.2)
                        last_angles[idx] = curr_angle

                        forge.update_vertices(size)
                        forge.project_and_draw(frame, data["render_pos"][0], data["render_pos"][1], 
                                               curr_angle, 0, color=color)
                        
                        cv2.putText(frame, label, (data["render_pos"][0]-20, data["render_pos"][1]+40), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # HUD Superior
            status_color = FUSION_COLOR if fusion_enabled else (0, 255, 0)
            status_msg = "FUSION LOCKED" if fusion_enabled else "STANDBY"
            cv2.putText(frame, f"AGAMOTTO-OS | STATUS: {status_msg}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)

            cv2.imshow("Agamotto-OS v3.1", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        eye.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    start_agamotto()