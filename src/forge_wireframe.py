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
        
    def project_and_draw(self, frame, center_x, center_y, angle_y, angle_x=0):
        """
        Pega os vértices 3D, aplica rotação/translação, projeta para 2D
        e desenha as linhas no frame.
        """
        # 2. A MÁGICA DO MANUSEIO: MATRIZES DE ROTAÇÃO
        # Rotação no eixo Y (girar a mão para os lados)
        theta_y = np.radians(angle_y)
        c_y, s_y = np.cos(theta_y), np.sin(theta_y)
        rotation_y = np.array([
            [c_y, 0, s_y],
            [0, 1, 0],
            [-s_y, 0, c_y]
        ])
        
        # Rotação no eixo X (inclinar a mão para frente/trás - opcional)
        theta_x = np.radians(angle_x)
        c_x, s_x = np.cos(theta_x), np.sin(theta_x)
        rotation_x = np.array([
            [1, 0, 0],
            [0, c_x, -s_x],
            [0, s_x, c_x]
        ])
        
        # Matriz de rotação combinada (Y depois X)
        rotation_matrix = np.dot(rotation_x, rotation_y)
        
        # 3. TRANSFORMAÇÃO E PROJEÇÃO (3D -> 2D)
        projected_points = []
        
        for vertex in self.vertices:
            # a. Rotacionar o vértice na origem
            rotated_vertex = np.dot(rotation_matrix, vertex)
            
            # b. Transladar (Mover para o centro da palma na tela)
            # O OpenGL projeta Z para "trás". Vamos simular profundidade (Perspectiva)
            z_depth = 500 # Fator de profundidade virtual
            
            # Matriz de Projeção Perspectiva Simplificada:
            # x' = x / (z + profundidade), y' = y / (z + profundidade)
            z_factor = 1 / (rotated_vertex[2] + z_depth)
            
            # Coordenadas 2D projetadas, centralizadas na palma
            px = int(rotated_vertex[0] * z_depth * z_factor) + center_x
            py = int(rotated_vertex[1] * z_depth * z_factor) + center_y
            
            projected_points.append((px, py))
            
        # 4. DESENHAR AS ARESTAS (LINHAS)
        # Vamos usar o Verde "Agamotto" (0, 255, 0)
        color = (0, 255, 0)
        thickness = 2
        
        for edge in self.edges:
            p1 = projected_points[edge[0]]
            p2 = projected_points[edge[1]]
            
            # OpenCV desenha linhas 2D puras
            cv2.line(frame, p1, p2, color, thickness, cv2.LINE_AA)
            
        # Opcional: Desenhar pontos nos vértices
        for point in projected_points:
            cv2.circle(frame, point, 3, (255, 255, 255), -1)