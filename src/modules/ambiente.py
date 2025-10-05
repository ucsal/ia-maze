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
                    self.mapa[y][x] = 'S' # Coloca o agente no mapa
                    return [x, y]
        return None # Retorna None se a entrada 'E' não for encontrada

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

