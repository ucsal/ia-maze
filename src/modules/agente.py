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
        
        # A memória do agente sobre o mapa. Dicionário: (x, y) -> caractere
        self.memoria = {}
        self.historico_posicoes = [(self.x, self.y)] # Para gerar o vídeo

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

    def _decidir_proxima_acao(self, visao):
        """
        Lógica de decisão do agente mais robusta para evitar loops.
        """
        # --- Dicionários de ajuda ---
        rotacao_direita = {'N': 'L', 'L': 'S', 'S': 'O', 'O': 'N'}
        rotacao_esquerda = {'N': 'O', 'O': 'S', 'S': 'L', 'L': 'N'}
        frente = {'N': (0, -1), 'S': (0, 1), 'L': (1, 0), 'O': (-1, 0)}

        # Função auxiliar para verificar se uma célula está livre
        def verificar_celula(direcao):
            dx, dy = frente[direcao]
            return self.memoria.get((self.x + dx, self.y + dy)) != 'X'

        # --- Lógica de Decisão Hierárquica ---

        # Objetivo 1: Se todas as comidas foram coletadas, buscar a saída 'S'
        if self.comidas_coletadas == self.total_comidas_no_mapa:
            for i in range(3):
                for j in range(3):
                    if visao[i][j] == 'S':
                        # Se a saída está adjacente, move-se para ela
                        if j == 1 and i == 0: self.setDirection('N'); self.move(); return
                        if j == 1 and i == 2: self.setDirection('S'); self.move(); return
                        if j == 0 and i == 1: self.setDirection('O'); self.move(); return
                        if j == 2 and i == 1: self.setDirection('L'); self.move(); return

        # Objetivo 2: Procurar por comida na visão imediata
        for i in range(3):
            for j in range(3):
                if visao[i][j] == 'o':
                    # Se a comida está adjacente, move-se para ela
                    if j == 1 and i == 0: self.setDirection('N'); self.move(); return
                    if j == 1 and i == 2: self.setDirection('S'); self.move(); return
                    if j == 0 and i == 1: self.setDirection('O'); self.move(); return
                    if j == 2 and i == 1: self.setDirection('L'); self.move(); return

        # Objetivo 3: Explorar usando a regra da "mão direita" de forma mais segura
        dir_a_direita = rotacao_direita[self.direcao]
        dir_a_frente = self.direcao
        dir_a_esquerda = rotacao_esquerda[self.direcao]

        if verificar_celula(dir_a_direita):
            # 1. Se o caminho à direita está livre, vira e move
            self.setDirection(dir_a_direita)
            self.move()
        elif verificar_celula(dir_a_frente):
            # 2. Senão, se o caminho à frente está livre, move
            self.move()
        else:
            # 3. Senão, apenas vira à esquerda (fica pronto para o próximo passo)
            # Em um beco sem saída, ele vai virar à esquerda até encontrar um caminho.
            self.setDirection(dir_a_esquerda)
        
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