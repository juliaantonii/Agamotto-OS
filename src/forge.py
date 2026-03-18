import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Definição Matemática do Cubo
# 8 vértices (x, y, z) centrados na origem (0,0,0)
vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

# 12 arestas que conectam os vértices
edges = (
    (0,1), (0,3), (0,4),
    (2,1), (2,3), (2,7),
    (6,3), (6,4), (6,7),
    (5,1), (5,4), (5,7)
)

# Cores para as arestas (opcional, para dar profundidade)
# R, G, B para cada aresta. Vamos usar verde "Agamotto"
edge_colors = [(0, 1, 0) for _ in range(len(edges))]

class AgamottoForge:
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        
        # Configurar a Projeção OpenGL (como a câmera 3D vê o mundo)
        # gluPerspective(fovy, aspect, zNear, zFar)
        # Um FOV (campo de visão) de 45 é padrão.
        gluPerspective(45, (display_width/display_height), 0.1, 50.0)
        
        # Variáveis de rotação do cubo
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0

    def set_rotation(self, rx, ry, rz):
        """Atualiza a rotação do cubo baseado na mão."""
        self.rot_x = rx
        self.rot_y = ry
        self.rot_z = rz

    def draw_cube(self):
        """Desenha as arestas do cubo com a rotação atual."""
        glBegin(GL_LINES)
        for edge in edges:
            for vertex_idx in edge:
                # Opcional: Colorir arestas
                # glColor3fv(edge_colors[edges.index(edge)])
                # glColor3f(0, 1, 0) # Verde fixo
                glVertex3fv(vertices[vertex_idx])
        glEnd()

    def render_scene(self, hand_position_x, hand_position_y):
        """Desenha o frame 3D."""
        # Limpar o buffer de cor e profundidade
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # Carregar a matriz identidade para resetar transformações
        glLoadIdentity()
        
        # --- A MÁGICA DO MANUSEIO ---
        
        # 1. Translação (Ajustar a posição do cubo para a câmera 3D)
        # O OpenGL coloca a câmera em (0,0,0). Precisamos mover o cubo "para frente" (z negativo)
        # e alinhá-lo com as coordenadas da câmera 2D (normalizadas).
        glTranslate(hand_position_x, hand_position_y, -10) # Movemos -10 no Z
        
        # 2. Rotação (Girar o cubo conforme a mão)
        glRotatef(self.rot_x, 1, 0, 0) # Rotação no eixo X
        glRotatef(self.rot_y, 0, 1, 0) # Rotação no eixo Y
        glRotatef(self.rot_z, 0, 0, 1) # Rotação no eixo Z
        
        # 3. Desenhar o cubo
        self.draw_cube()
        
        # Atualizar o display (trocar o buffer)
        pygame.display.flip()