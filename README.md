# _Agamotto-OS_

> **Status**: Experimental (Phase 2: Multi-Hand Logic)  
> **Core**: Python | MediaPipe | OpenCV | NumPy

**Agamotto-OS** é um sistema de visão computacional desenvolvido para simular interfaces holográficas através de rastreamento manual de alta precisão. O projeto transforma gestos físicos em comandos de manipulação geométrica 3D em tempo real.

São testes iniciais para um projeto maior futuro.

---

## _Funcionalidades Atuais_

- **Neural Hand Tracking**: Rastreamento esquelético via MediaPipe.
- **Void-Forge Engine**: Renderização de wireframes 3D projetados sobre o espaço 2D da câmera.
- **Pinch-to-Scale**: Manipulação dinâmica de tamanho através da distância entre o polegar e o indicador.
- **Perspective Projection**: Cálculo de matrizes para rotação e profundidade (X, Y, Z).

---

## _Estrutura do Projeto_

O repositório segue um fluxo de desenvolvimento baseado em ramificações (branches) para garantir a estabilidade do núcleo:

- `main`: Versão estável com interação básica (v1.0).
- `feat/dual-hand-logic`: Implementação de suporte para múltiplas mãos.
- `docs/`: Galeria de testes e documentação técnica.

---

## _Como Executar_

```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/Agamotto-OS.git](https://github.com/seu-usuario/Agamotto-OS.git)

# Instale as dependências
pip install opencv-python mediapipe numpy

# Inicie o sistema
python src/main.py