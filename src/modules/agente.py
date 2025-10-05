import time
import os

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
        self.historico_posicoes = [(self.x, self.y)] # Para gerar o vídeo
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
            self.historico_posicoes.append((self.x, self.y)) # Guarda para o vídeo
            
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