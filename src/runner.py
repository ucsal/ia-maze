import time
import os

ARQUIVO_LABIRINTO = os.path.join(os.path.dirname(__file__), "..", "labirinto.txt")


class Agente:
    """
    O agente que explora o labirinto. Possui sensores, atuadores,
    memória e uma estratégia de decisão.
    """

    def __init__(self, ambiente, total_comidas):
        self.ambiente = ambiente
        self.x, self.y = self.ambiente.posicao_agente
        self.direcao = 'S'  # 'N', 'S', 'L', 'O'

        self.total_comidas_no_mapa = total_comidas
        self.comidas_coletadas = 0
        self.passos = 0

        self.memoria = {}
        self.historico_posicoes = [(self.x, self.y)]  # Para gerar o vídeo
        self.contagem_visitas = {}

    # --- SENSOR ---
    def getSensor(self):
        visao = self.ambiente.get_sensor_info(self.x, self.y)

        # Atualiza a memória com base na visão atual
        for i in range(-1, 2):
            for j in range(-1, 2):
                mapa_y = self.y + i
                mapa_x = self.x + j

                visao_y = i + 1
                visao_x = j + 1

                if (mapa_x, mapa_y) not in self.memoria:
                    self.memoria[(mapa_x, mapa_y)] = visao[visao_y][visao_x]
        return visao

    # --- ATUADORES ---
    def setDirection(self, nova_direcao):
        """Define a nova direção do agente."""
        if nova_direcao in ['N', 'S', 'L', 'O']:
            self.direcao = nova_direcao
            # Atualiza o caractere no mapa para refletir a nova direção
            self.ambiente.mapa[self.y][self.x] = self.direcao
        else:
            print(f"Atenção: Direção inválida '{nova_direcao}'")

    def move(self):
        """
        Move o agente uma posição para frente, na direção atual.
        Retorna True se o movimento foi bem-sucedido, False caso contrário.
        """
        futuro_x, futuro_y = self.x, self.y
        if self.direcao == 'N':
            futuro_y -= 1
        elif self.direcao == 'S':
            futuro_y += 1
        elif self.direcao == 'O':
            futuro_x -= 1
        elif self.direcao == 'L':
            futuro_x += 1

        # O agente consulta sua própria memória para decidir se pode se mover
        celula_alvo = self.memoria.get((futuro_x, futuro_y), 'desconhecido')

        if celula_alvo != 'X':
            x_antigo, y_antigo = self.x, self.y
            self.x, self.y = futuro_x, futuro_y
            self.contagem_visitas[(self.x, self.y)] = self.contagem_visitas.get((self.x, self.y), 0) + 1

            self.passos += 1

            # Atualiza o ambiente com a nova posição
            self.ambiente.mover_agente(x_antigo, y_antigo, self.x, self.y, self.direcao)
            self.historico_posicoes.append((self.x, self.y))  # Guarda para o vídeo

            # Verifica se há comida na nova posição
            if self.memoria.get((self.x, self.y)) == 'o':
                self.comidas_coletadas += 1
                print(f"Comida encontrada! Total: {self.comidas_coletadas}/{self.total_comidas_no_mapa}")
                # Atualiza a memória para refletir que a comida foi consumida
                self.memoria[(self.x, self.y)] = '_'

            return True
        else:
            return False

    # Dentro da classe Agente
    def _decidir_proxima_acao(self, visao):
        """
        LÓGICA DE DECISÃO AVANÇADA
        O agente lida com o mapa ambíguo e usa contagem de visitas para evitar loops.
        """
        # --- Dicionários de ajuda ---
        frente = {'N': (0, -1), 'S': (0, 1), 'L': (1, 0), 'O': (-1, 0)}
        direcoes_possiveis = ['N', 'S', 'L', 'O']

        # --- REGRA DE INTERPRETAÇÃO DE TERRENO ---
        def celula_esta_livre(x, y):
            celula = self.memoria.get((x, y))
            if celula == 'X':
                return False  # Parede é sempre bloqueada
            # REGRA PRINCIPAL: 'S' é tratado como parede se ainda houver comida.
            if celula == 'S' and self.comidas_coletadas < self.total_comidas_no_mapa:
                return False  # 'S' é uma parede temporária
            return True

        # --- LÓGICA DE DECISÃO HIERÁRQUICA ---

        # Objetivo 1 e 2: Se comida ou saída (e todas as comidas foram coletadas)
        # estiverem adjacentes, ir diretamente para elas. Esta é uma ação reativa.
        for direcao in direcoes_possiveis:
            dx, dy = frente[direcao]
            px, py = self.x + dx, self.y + dy
            celula_alvo = self.memoria.get((px, py))

            if celula_alvo == 'o':
                self.setDirection(direcao)
                self.move()
                return

            if celula_alvo == 'S' and self.comidas_coletadas == self.total_comidas_no_mapa:
                self.setDirection(direcao)
                self.move()
                return

        # --- Objetivo 3: EXPLORAÇÃO INTELIGENTE BASEADA EM MEMÓRIA ---
        # Escolhe a direção que leva à célula menos visitada.

        movimentos_validos = []
        for direcao in direcoes_possiveis:
            dx, dy = frente[direcao]
            px, py = self.x + dx, self.y + dy
            if celula_esta_livre(px, py):
                contagem = self.contagem_visitas.get((px, py), 0)
                movimentos_validos.append((direcao, contagem))

        if not movimentos_validos:
            self.setDirection('N')  # Apenas uma direção padrão para não travar
            return

        movimentos_validos.sort(key=lambda item: item[1])
        # A melhor direção é a primeira da lista ordenada
        melhor_direcao = movimentos_validos[0][0]

        self.setDirection(melhor_direcao)
        self.move()

    def executar(self):
        """
        Ciclo de vida principal do agente: percebe, decide e atua.
        """
        print("Iniciando a jornada do agente...")
        while True:
            # Limpa a tela para uma visualização mais limpa no terminal
            os.system('cls' if os.name == 'nt' else 'clear')

            # 1. SENSOR: Perceber o ambiente e atualizar a memória
            visao_atual = self.getSensor()

            # Imprime o estado atual
            print(self.ambiente)
            print(f"Posição: ({self.x}, {self.y}) | Direção: {self.direcao}")
            print(f"Passos: {self.passos} | Comidas: {self.comidas_coletadas}/{self.total_comidas_no_mapa}")

            # Condição de parada
            if self.comidas_coletadas == self.total_comidas_no_mapa and \
                    self.memoria.get((self.x, self.y)) == 'S':
                print("\nObjetivo alcançado! Todas as comidas foram coletadas e o agente chegou à saída.")
                break

            # 2. DECISÃO: Escolher a próxima ação
            self._decidir_proxima_acao(visao_atual)

            # Pausa para visualização
            time.sleep(0.1)

        # Cálculo da pontuação final
        pontuacao = (self.comidas_coletadas * 10) - self.passos
        print("\n--- Simulação Finalizada ---")
        print(f"Total de comidas coletadas: {self.comidas_coletadas}")
        print(f"Total de passos dados: {self.passos}")
        print(f"Pontuação Final: ({self.comidas_coletadas} * 10) - {self.passos} = {pontuacao} pontos")


class Ambiente:
    """
    Representa o labirinto. Carrega o mapa de um arquivo e fornece
    informações sensoriais para o agente.
    """

    def __init__(self, arquivo_path):
        self.mapa = self._carregar_mapa(arquivo_path)
        self.altura = len(self.mapa)
        self.largura = len(self.mapa[0])
        self.posicao_agente = self._encontrar_posicao_inicial()
        self.total_comidas = self._contar_comidas()
        print(f"Ambiente criado. Tamanho: {self.largura}x{self.altura}. Comidas: {self.total_comidas}.")

    def _carregar_mapa(self, arquivo_path):
        """Carrega o labirinto de um arquivo TXT para uma matriz de caracteres."""
        with open(arquivo_path, 'r') as f:
            # strip() remove espaços em branco e quebras de linha no início/fim
            return [list(line.strip()) for line in f.readlines()]

    def _encontrar_posicao_inicial(self):
        """Encontra a posição inicial do agente ('E') no mapa."""
        for y, linha in enumerate(self.mapa):
            for x, celula in enumerate(linha):
                if celula == 'E':
                    # Inicialmente, o agente não tem uma direção definida no mapa.
                    # Vamos assumir que ele começa virado para o Sul ('S').
                    self.mapa[y][x] = 'S'  # Coloca o agente no mapa
                    return [x, y]
        return None  # Retorna None se a entrada 'E' não for encontrada

    def _contar_comidas(self):
        """Conta o número total de comidas ('o') no mapa."""
        count = 0
        for linha in self.mapa:
            count += linha.count('o')
        return count

    def get_sensor_info(self, x, y):
        """
        Retorna uma matriz 3x3 da visão do agente.
        Posições fora do mapa são consideradas paredes 'X'.
        """
        matriz_visao = [['X' for _ in range(3)] for _ in range(3)]

        # Mapeia as coordenadas do agente para o centro da matriz de visão (1,1)
        for i in range(-1, 2):  # Linhas: -1, 0, 1
            for j in range(-1, 2):  # Colunas: -1, 0, 1
                mapa_y = y + i
                mapa_x = x + j

                visao_y = i + 1
                visao_x = j + 1

                if 0 <= mapa_y < self.altura and 0 <= mapa_x < self.largura:
                    matriz_visao[visao_y][visao_x] = self.mapa[mapa_y][mapa_x]

        return matriz_visao

    def mover_agente(self, x_antigo, y_antigo, x_novo, y_novo, direcao_agente):
        """Atualiza a posição do agente no mapa."""
        # Se o agente saiu da posição de uma comida, ela é consumida (vira corredor)
        if self.mapa[y_antigo][x_antigo] not in ['E', 'S']:
            self.mapa[y_antigo][x_antigo] = '_'

        self.mapa[y_novo][x_novo] = direcao_agente
        self.posicao_agente = [x_novo, y_novo]

    def consumir_comida(self, x, y):
        """Marca uma comida como consumida (transforma em corredor)."""
        # A lógica de mover o agente já faz isso, mas podemos ter uma função explícita
        self.mapa[y][x] = '_'

    def __str__(self):
        """Retorna uma representação do mapa como string para impressão."""
        return "\n".join(["".join(linha) for linha in self.mapa])


import os




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
            COR_COMIDA = (0, 215, 255)  # Dourado
            COR_ENTRADA = (0, 128, 0)  # Verde
            COR_SAIDA = (0, 0, 255)  # Vermelho
            COR_AGENTE = (255, 0, 0)  # Azul
            COR_RASTRO = (200, 150, 150)  # Azul claro

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
                        if cell == 'X':
                            cor = COR_PAREDE
                        elif cell == 'o':
                            cor = COR_COMIDA
                        elif cell == 'E':
                            cor = COR_ENTRADA
                        elif cell == 'S':
                            cor = COR_SAIDA

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