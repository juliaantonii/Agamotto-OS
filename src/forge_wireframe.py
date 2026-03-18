import cv2
import numpy as np

class AgamottoForgeWireframe:
    # Adicione ou verifique se este método existe dentro da classe AgamottoForgeWireframe
    def update_vertices(self, new_size):
        self.size = new_size
        s = new_size / 2
        # Recalcula os 8 pontos do cubo com o novo tamanho
        self.vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s],  [s, -s, s],  [s, s, s],  [-s, s, s]
        ])
        
    def __init__(self, screen_width, screen_height, cube_size=100):
        self.w = screen_width
        self.h = screen_height
        self.size = cube_size
        
        # 1. DEFINIÇÃO MATEMÁTICA DO CUBO (Wireframe)
        # 8 vértices (x, y, z) centrados na origem (0,0,0)
        s = cube_size / 2 # Metade do tamanho para centrar
        self.vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s], # Frente (z negativo)
            [-s, -s, s],  [s, -s, s],  [s, s, s],  [-s, s, s]   # Trás (z positivo)
        ])
        
        # 12 arestas (índices dos vértices a conectar)
        self.edges = [
            (0,1), (1,2), (2,3), (3,0), # Quadrado Frente
            (4,5), (5,6), (6,7), (7,4), # Quadrado Trás
            (0,4), (1,5), (2,6), (3,7)  # Linhas de conexão
        ]
        
    def project_and_draw(self, frame, center_x, center_y, angle_y, angle_x=0, color=(0, 255, 0)):
        # 1. Rotação (Exemplo simplificado de lógica que você já deve ter)
        theta = np.radians(angle_y)
        c, s = np.cos(theta), np.sin(theta)
        rotation_matrix = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

        projected_points = []
        for vertex in self.vertices:
            # Rotacionar
            rotated = np.dot(rotation_matrix, vertex)
            # Projetar (ajuste os valores de perspectiva se necessário)
            z_factor = 200 / (rotated[2] + 400)
            px = int(rotated[0] * z_factor) + center_x
            py = int(rotated[1] * z_factor) + center_y
            projected_points.append((px, py))

        # 2. Desenhar as Arestas com a COR DINÂMICA
        for edge in self.edges:
            p1 = projected_points[edge[0]]
            p2 = projected_points[edge[1]]
            # O SEGREDO ESTÁ AQUI: Usar a variável 'color' que recebemos
            cv2.line(frame, p1, p2, color, 2, cv2.LINE_AA)