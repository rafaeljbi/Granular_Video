# Granular_Video: Análise Comparativa de Modelos de Classificação e Detecção para Reconhecimento de Produtos

Este repositório contém o código e a análise de parte da dissertação de mestrado [Reconhecimento Granular em Conteúdo de Vídeos Não-Controlados].

## Objetivo

O objetivo central deste projeto é investigar a performance de diferentes abordagens de visão computacional para o reconhecimento de produtos específicos (SKUs) em vídeos "in-the-wild" (vídeos não controlados, como os do YouTube).

Nesse momento nos deparamos com uma questão de pesquisa: para o reconhecimento de produtos, é mais eficaz treinar um modelo de **detecção de objetos** (com bounding boxes) ou um modelo de **classificação** (sem bounding boxes) mais simples e especialista?

Este repositório compara diretamente essas duas abordagens usando o framework [YOLOv8](https://www.ultralytics.com/yolo).

## Metodologia

O experimento foi conduzido em três etapas principais: Treinamento dos modelos, Coleta de dados em vídeos de teste e Análise de performance frame-a-frame.

### 1. Os Modelos Concorrentes

Dois modelos foram treinados para servirem como nossos "concorrentes":

* **Modelo 1: Generalista (Classificação Pura)**
    * **Arquivo:** [best3_no_annotation.pt](https://github.com/rafaeljbi/Granular_Video/blob/main/Best_models/best3_no_annotation.pt)
    * **Arquitetura:** YOLOv8-Cls (Classificação, sem os bounding boxes).
    * **Treino:** Treinado em um dataset de imagens de produtos (frames extraídos do dataset [VERD](https://www.mdpi.com/1424-8220/23/1/513)) sem anotações de *bounding box*. O objetivo deste modelo é classificar o *frame inteiro*.
    * **Hipótese:** Ser mais rápido e talvez mais robusto a oclusões, já que não depende de uma "caixa" visível.

* **Modelo 2: Especialista (Detecção de Objetos)**
    * **Arquivo:** [best4_with_annotation.pt](https://github.com/rafaeljbi/Granular_Video/blob/main/Best_models/best4_with_annotation.pt)
    * **Arquitetura:** YOLOv8-Detect (Detecção).
    * **Treino:** Treinado no mesmo dataset [VERD](https://www.mdpi.com/1424-8220/23/1/513)), mas utilizando anotações de *bounding box* (feitas com o [Roboflow](https://roboflow.com/)).
    * **Hipótese:** Ser mais preciso, pois foi explicitamente treinado para *localizar* o objeto no frame, reduzindo o ruído do plano de fundo.

### 2. O Dataset de Teste (In-the-Wild)

Para testar os modelos em um cenário realista, foram utilizados vídeos de reviews de produtos do YouTube. Para cada uma das 5 classes-alvo, um vídeo foi selecionado e seus primeiros 2 minutos foram analisados:

* **[Smartwatch](https://www.youtube.com/watch?v=2w4EkcEH8jU&t=330s)** 

* **[Hair Dryer](https://www.youtube.com/watch?v=P3rPEoy82Uk)** 
 
* **[Mixer](https://www.youtube.com/watch?v=z7mW82k8Vp4)** 
   
* **[Blender](https://www.youtube.com/watch?v=M8B00ELaMtg)** 
     
* **[Grain Grinder](https://www.youtube.com/watch?v=ZeBEq7a2mgI)** 

Os primeiros minutos foram coletados com o script [Download_videos_120sec.py](https://github.com/rafaeljbi/Granular_Video/blob/main/Comparison/Download_videos_120sec.py) e estão armazenados em [Videos_comparison](https://github.com/rafaeljbi/Granular_Video/tree/main/Comparison/Videos_comparison).

### 3. A Avaliação

A performance não foi medida apenas pela acurácia, mas por uma análise granular frame-a-frame:

1.  **Coleta de Dados:** Os dois modelos foram executados em todos os frames dos vídeos de teste, gerando um log (CSV) com o `Timestamp`, `Modelo` e `Classe` detectada.
   Além disso, foi usado o threshold de 50% (`CONFIDENCE_THRESHOLD = 0.5`) para ambos os modelos.
3.  **Geração do Ground Truth:** Foi criado um "gabarito" (ground truth) manual, onde cada frame foi anotado por um humano (usando o script [Ground_truth_generation_video-check.py](https://github.com/rafaeljbi/Granular_Video/blob/main/Comparison/Ground_truth_generation_video-check.py)) para registrar a presença *real* do objeto.
4.  **Análise:** Os logs dos modelos foram comparados contra o ground truth frame-a-frame (considerando um "frame" como um intervalo de ~0.033s). Métricas de **Precision**, **Recall** e **F1-Score** foram calculadas para determinar qual modelo foi o vencedor para cada classe.

## Resultados

A análise comparou o desempenho dos dois modelos em relação ao ground truth. Os resultados completos podem ser encontrados no notebook [Comparison_Notebook.ipynb](https://github.com/rafaeljbi/Granular_Video/blob/main/Comparison/Comparison_Notebook.ipynb). Além disso, os dados gerados pelo notebbok estão compilados no diretório [Resultados_Analise_Frame_a_Frame](https://github.com/rafaeljbi/Granular_Video/tree/main/Comparison/Resultados_Analise_Frame_a_Frame).

### Análise Quantitativa (Métricas)

A tabela abaixo resume o F1-Score médio de cada modelo em todas as classes:

**Smartwatch:**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Especialista | 0.588 | 0.443 | 0.871 |
| Geral | 0.538 | 0.431 | 0.717 |

**Interpretação:**
O modelo 'Especialista' (F1=0.588) superou o 'Geral' (F1=0.538). Isso se deveu principalmente ao seu **Recall** (87,1%) muito superior, indicando que ele foi muito mais eficaz em *encontrar* o objeto. No entanto, ambos os modelos sofreram com baixa **Precisão** (~44%), gerando um número significativo de Falsos Positivos.

### Análise Qualitativa

Os gráficos de linha do tempo mostram *quando* cada modelo acertou, errou ou se confundiu com outra classe. As cores representam a classe detectada em cada frame.

**Smartwatch: Linha do Tempo Categórica**
<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/b1a0ff35-cb06-4da2-879b-20fe94f86ec7" />

**Interpretação:** O gráfico acima ilustra visualmente os Falsos Positivos. Perceba que em vários momentos (ex: entre 9.2s e 9.4s), o Ground Truth é `None` (branco), mas o modelo 'Especialista' detecta `Grain_grinder` (laranja) e `Mixer` (verde). Isso expõe a "confusão" do modelo de classificação, algo que as métricas binárias não mostram.


### Matrizes de Confusão

As matrizes de confusão (calculadas para a classe-alvo de cada vídeo) ajudam a visualizar a contagem de Verdadeiros Positivos (TP), Falsos Positivos (FP) e Falsos Negativos (FN) em nível de frame.

**Smartwatch: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**
<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/8c2345c7-45de-401b-8c47-164b06844f6e" />

**Smartwatch: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**
<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/442e910e-1c9f-4d00-9dee-cff724ab2ef7" />


## Como Replicar o Experimento

Este repositório está estruturado para permitir a replicação completa da análise. Para isso serão necessáriuos alguns ajustes e configurações nos caminhos dos arquivos.

### 1. Configuração do Ambiente

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/rafaeljbi/Granular_Video.git](https://github.com/rafaeljbi/Granular_Video.git)
    cd Granular_Video
    ```
2.  (Recomendado) Crie um ambiente virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Instale as dependências:
    *(Nota: Você precisará criar este arquivo `requirements.txt` primeiro, rodando `pip freeze > requirements.txt` no seu ambiente que funciona)*
    ```bash
    pip install -r requirements.txt
    ```
    As bibliotecas principais são `ultralytics`, `pandas`, `opencv-python`, `matplotlib`, `seaborn` e `yt-dlp`. Você também precisará do [FFmpeg](https://ffmpeg.org/download.html) instalado no PATH do seu sistema.

### 2. Coleta de Dados dos Modelos

Para gerar os logs de detecção a partir de um vídeo do YouTube:
* Use o script `Frame_read.py`. *(Você pode renomear o script que fizemos para este nome)*
* Configure as URLs e caminhos dos modelos dentro do script.
* Execute: `python Frame_read.py`
* Isso irá gerar os arquivos `log_...txt`.

### 3. Geração do Ground Truth Manual

Para gerar o "gabarito" manual dos vídeos:
* Primeiro, baixe os vídeos de 2 minutos usando `Download_videos_120sec.py`.
* Em seguida, use o script `Ground_truth_generation_video-check.py`.
* Configure o `VIDEO_FOLDER` e o `CLASS_KEYS` no script.
* Execute: `python Ground_truth_generation_video-check.py`
* Uma janela do OpenCV será aberta. Pressione as teclas (`1`, `2`, `3`...) correspondentes à classe visível. Pressione `ESPAÇO` para pausar/despausar.
* Isso irá gerar os arquivos `Ground_truth_...txt`.

### 4. Análise e Geração de Gráficos

Para gerar as métricas, tabelas e gráficos:
* Execute o Jupyter Notebook `Analise_Resultados.ipynb`. *(Recomendado: Use o Google Colab para evitar conflitos de biblioteca)*.
* Certifique-se de que todos os 10 arquivos `.txt` (5 de log, 5 de ground truth) estejam na pasta correta (ex: `Comparison_files/`).
* Execute todas as células do notebook.
* Os resultados (`.csv` e `.png`) serão salvos na pasta `Resultados_Analise_Frame_a_Frame/`.
