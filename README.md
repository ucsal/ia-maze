-   **`.python-version`**: Arquivo que especifica a versão do Python para o projeto (`3.11.9`).
-   **`labirinto.txt`**: Arquivo de texto que define o mapa do labirinto a ser explorado.
-   **`requirements.txt`**: Lista as dependências de pacotes Python.
-   **`src/main.py`**: O script principal que inicializa e executa a simulação.
-   **`modules/`**: Diretório contendo as classes principais do projeto.
    -   `agente.py`: Implementação da classe `Agente`.
    -   `ambiente.py`: Implementação da classe `Ambiente`.

## Pré-requisitos

Para executar este projeto, você precisará ter o Python instalado na versão exata especificada.

-   **Python 3.11.9**

## Configuração do Ambiente

O projeto utiliza um ambiente virtual (`venv`) para gerenciar suas dependências de forma isolada. Siga os passos abaixo para configurar seu ambiente.

1.  **Clone o repositório** (se aplicável) e navegue até o diretório raiz do projeto.

2.  **Crie o ambiente virtual:**
    ```bash
    python -m venv venv
    ```

3.  **Ative o ambiente virtual:**

    -   **No Windows (PowerShell/CMD):**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **No macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    Após a ativação, você verá `(venv)` no início do seu prompt de comando.

4.  **Instale as dependências:**
    Com o ambiente ativado, instale as bibliotecas necessárias listadas no `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

Certifique-se de que seu ambiente virtual esteja ativado. O script principal a ser executado está localizado dentro do diretório `src`.

**Execute o programa a partir do diretório raiz do projeto** usando o seguinte comando:

```bash
python src/main.py
```