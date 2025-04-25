# CarDetector

## Descrição do Projeto

Este repositório contém o código de um sistema inteligente para a contagem de veículos em um semáforo, com o objetivo de otimizar o tempo de semáforo e entender padrões de tráfego ao longo do dia. O sistema conta a quantidade exata de carros que passam por um determinado ponto da via, sem a necessidade de sensores físicos, levando em consideração os tempos de sinal vermelho e verde para evitar contagens duplicadas.

## Etapas de Execução

### 1. Ter o Python Instalado

Certifique-se de ter o Python instalado em sua máquina. Você pode verificar se o Python está instalado digitando o seguinte comando no terminal:

```bash
python --version
```

Caso não tenha o Python, baixe e instale [aqui](https://www.python.org/downloads/).

### 2. Criar uma Venv (Ambiente Virtual)

Crie um ambiente virtual para evitar conflitos de dependências:

```bash
python -m venv venv
```

### 3. Iniciar a Venv

- **Windows**:

```bash
venv\Scripts\activate
```

- **Linux/Mac**:

```bash
source venv/bin/activate
```

### 4. Instalar as Dependências

Dentro do ambiente virtual, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

### 5. Executar o Streamlit

Para rodar a aplicação, basta executar o seguinte comando:

```bash
streamlit run main.py
```

## Como Funciona a Aplicação

1. **Carregar o Vídeo**:
   Ao iniciar, o usuário entra na página para adicionar um novo vídeo para processamento. O formato de vídeo aceito atualmente é MP4 (por questões de tempo de processamento). Para o futuro, será implementado o suporte a outros tipos de vídeos.

2. **Configurações**:
   Após abrir o vídeo, um frame aleatório do vídeo é exibido à esquerda. À direita, o usuário pode configurar dois pontos para traçar uma linha (que será usada para contar os veículos que atravessam). O usuário também pode configurar:
   - Confiança do modelo de detecção (conf)
   - IOU (intersection over union)
   - Modelo do Tracker
   - Tempo do sinal verde e vermelho

   Após definir todas as configurações, o usuário pode iniciar o processamento do vídeo.

   ![**Imagem da página de configuração em** `/images/detect_page.png`](/images/detect_page.png)

3. **Página de Resultados**:
   Após o processamento, o usuário pode acessar a página de resultados, onde verá:
   - A primeira coluna exibe o vídeo com boxes de identificação (preto: carro não passou pela linha, verde: passou durante sinal verde, vermelho: passou durante sinal vermelho).
   - A segunda coluna contém as métricas gerais, como:
     - Total de veículos detectados
     - Veículos que passaram no sinal verde
     - Veículos que passaram no sinal vermelho
     - O grau de confiança do modelo
     - IOU
     - Modelo utilizado
     - Dois gráficos: um por valores totais acumulados e outro por valores temporais.
   - A terceira coluna oferece 4 botões para download:
     - Vídeo com detecção
     - CSV de detecção (contendo o ID e as posições dos carros)
     - CSV de métricas gerais (para gráficos)

   ![**Imagem da página de resultados em** `/images/result_page.png`](/images/result_page.png)

## Tecnologias Utilizadas

| Tecnologia            | Justificativa                                                                 |
|-----------------------|-------------------------------------------------------------------------------|
| `opencv-python`       | Biblioteca essencial para manipulação de frames de vídeo e operações de visão computacional, como detecção de objetos, manipulação de imagens e vídeos. |
| `streamlit`           | Framework para criação de interfaces web dinâmicas e interativas. Permite a construção de interfaces amigáveis e responsivas, facilitando a interação do usuário com o sistema. |
| `numpy`               | Utilizado para operações matemáticas e manipulação de arrays de dados, facilitando cálculos eficientes e rápidos, fundamentais para processamento de imagens e análise de dados. |
| `pandas`              | Para manipulação e análise de dados, incluindo a criação de tabelas e exportação. Pandas permite o gerenciamento eficiente de grandes volumes de dados de forma simples e poderosa. |
| `torch`               | Usado para acelerar o modelo de detecção YOLO, especialmente com aceleração de GPU. PyTorch é altamente eficiente em aprendizado profundo, possibilitando a execução rápida de modelos complexos em dispositivos com GPU. |
| `torchvision`         | Usado para manipulação e pré-processamento de imagens para redes neurais, além de ser uma excelente ferramenta para realizar transformações e aumentar a robustez do modelo de rede neural. |
| `ultralytics`         | **YOLOv8 foi escolhido pela sua eficiência e leveza**. Este modelo de detecção de objetos é amplamente utilizado devido à sua **alta precisão** e **baixa latência**. Eu já o utilizei em outros projetos e ele se mostrou adequado para a detecção em tempo real, sendo capaz de identificar veículos de forma rápida e eficiente, mesmo em ambientes urbanos com tráfego intenso. Além disso, o YOLOv8 possui **métodos nativos de tracking** que ajudam a acompanhar os objetos ao longo do tempo sem a necessidade de integração com bibliotecas externas de rastreamento. Isso torna o modelo **mais rápido e menos complexo** em termos de integração, além de simplificar a implementação de soluções para detecção e rastreamento. A leveza do modelo também contribui para um processamento mais rápido, sendo ideal para dispositivos que não possuem GPUs dedicadas, mas ainda assim conseguem fazer a execução de inferências em tempo hábil. |
| `altair`              | Utilizado para gerar gráficos interativos de visualização de dados. Essa ferramenta facilita a criação de gráficos dinâmicos e personalizáveis, o que foi essencial para a exibição das métricas de tráfego e veículos detectados ao longo do tempo. |

---
