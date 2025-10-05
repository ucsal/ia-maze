import os

from modules.ambiente import Ambiente
from modules.agente import Agente

ARQUIVO_LABIRINTO = os.path.join(os.path.dirname(__file__), "..",  "labirinto.txt")


# =============================================================================
# Programa Principal
# =============================================================================
if __name__ == "__main__":

    if not os.path.exists(ARQUIVO_LABIRINTO):
        print(f"Erro: O arquivo '{ARQUIVO_LABIRINTO}' não foi encontrado.")
    else:
        ambiente = Ambiente(ARQUIVO_LABIRINTO)
        agente = Agente(ambiente, ambiente.total_comidas)

        # 3. Inicia a simulação
        agente.executar()
        
        # 4. GERAÇÃO DO VÍDEO (requer bibliotecas externas)
        print("\nIniciando a geração do vídeo...")
        try:
            import cv2
            import numpy as np

            # --- Configurações do Vídeo ---
            LARGURA_CELULA = 40  # Tamanho de cada célula em pixels
            NOME_ARQUIVO_SAIDA = "jornada_do_agente.mp4"
            FPS = 10

            # --- Cores (em formato BGR para o OpenCV) ---
            COR_PAREDE = (80, 80, 80)
            COR_CORREDOR = (220, 220, 220)
            COR_COMIDA = (0, 215, 255) # Dourado
            COR_ENTRADA = (0, 128, 0) # Verde
            COR_SAIDA = (0, 0, 255) # Vermelho
            COR_AGENTE = (255, 0, 0) # Azul
            COR_RASTRO = (200, 150, 150) # Azul claro

            # --- Inicializa o vídeo ---
            mapa_inicial = Ambiente(ARQUIVO_LABIRINTO).mapa
            altura_mapa = len(mapa_inicial)
            largura_mapa = len(mapa_inicial[0])
            
            altura_frame = altura_mapa * LARGURA_CELULA
            largura_frame = largura_mapa * LARGURA_CELULA
            
            # Codec e criação do objeto VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            video_writer = cv2.VideoWriter(NOME_ARQUIVO_SAIDA, fourcc, FPS, (largura_frame, altura_frame))
            
            mapa_render = mapa_inicial.copy()
            
            for i, (x, y) in enumerate(agente.historico_posicoes):
                # Cria um frame em branco
                frame = np.zeros((altura_frame, largura_frame, 3), dtype=np.uint8)
                
                # Desenha o estado do mapa
                for row_idx, row in enumerate(mapa_render):
                    for col_idx, cell in enumerate(row):
                        cor = COR_CORREDOR
                        if cell == 'X': cor = COR_PAREDE
                        elif cell == 'o': cor = COR_COMIDA
                        elif cell == 'E': cor = COR_ENTRADA
                        elif cell == 'S': cor = COR_SAIDA

                        cv2.rectangle(
                            frame,
                            (col_idx * LARGURA_CELULA, row_idx * LARGURA_CELULA),
                            ((col_idx + 1) * LARGURA_CELULA, (row_idx + 1) * LARGURA_CELULA),
                            cor,
                            -1 
                        )
                
                # Desenha o rastro
                for hx, hy in agente.historico_posicoes[:i]:
                    cv2.rectangle(
                            frame,
                            (hx * LARGURA_CELULA, hy * LARGURA_CELULA),
                            ((hx + 1) * LARGURA_CELULA, (hy + 1) * LARGURA_CELULA),
                            COR_RASTRO,
                            -1 
                        )

                # Desenha o agente
                cv2.circle(
                    frame,
                    (x * LARGURA_CELULA + LARGURA_CELULA // 2, y * LARGURA_CELULA + LARGURA_CELULA // 2),
                    LARGURA_CELULA // 3,
                    COR_AGENTE,
                    -1
                )
                
                # Escreve o frame no arquivo de vídeo
                video_writer.write(frame)

                # Atualiza o mapa para o próximo frame (comida consumida)
                if mapa_render[y][x] == 'o':
                    mapa_render[y][x] = '_'

            video_writer.release()
            print(f"Vídeo '{NOME_ARQUIVO_SAIDA}' gerado com sucesso!")

        except ImportError:
            print("\nAVISO: As bibliotecas 'opencv-python' e 'numpy' não foram encontradas.")
            print("Para gerar o vídeo, instale-as com: pip install opencv-python numpy")