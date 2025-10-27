# Granular_Video: Análise Comparativa de Modelos de Classificação e Detecção para Reconhecimento de Produtos

Este repositório contém o código e a análise de parte da dissertação de mestrado **Reconhecimento Granular em Conteúdo de Vídeos Não-Controlados**.

**Autor**: Rafael Colen de Almeida

**Contato**: rafaeljbi@gmail.com

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

**1. Smartwatch:**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Geral | 0.588 | 0.443 | 0.871 |
| Especialista | 0.538 | 0.431 | 0.717 |

**Análise:**
O modelo 'Geral' (F1=0.588) superou o 'Especialista' (F1=0.538). Isso se deveu principalmente ao seu **Recall** (87,1%) muito superior, indicando que ele foi muito mais eficaz em *encontrar* o objeto. No entanto, ambos os modelos sofreram com baixa **Precisão** (~44%), gerando um número significativo de Falsos Positivos.

### Análise Qualitativa

Os gráficos de linha do tempo mostram *quando* cada modelo acertou, errou ou se confundiu com outra classe. As cores representam a classe detectada em cada frame.

**Smartwatch: Linha do Tempo Categórica**

<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/e88f368b-9c54-4004-9e65-cd10ff705546" />


**Análise:** O gráfico acima ilustra visualmente os problemas dos modelos.

A linha do Ground_Truth (topo, azul) mostra os períodos em que o smartwatch estava visível.

A linha do 'Geral' (baixo) é a mais caótica. Ela captura bem os blocos azuis do Ground Truth (alto Recall), mas nos períodos em branco (onde o objeto não estava) ela se torna extremamente "ruidosa", detectando incorretamente Grain Grinder (laranja), Hair Dryer (vermelho) e Mixer (verde). Isso explica sua baixíssima Precisão.

A linha do 'Especialista' (meio) também é ruidosa, mas visivelmente menos que a do 'Especialista'. Ela também mostra mais "buracos" brancos (Falsos Negativos) durante os períodos em que o Ground Truth estava ativo, validando seu Recall inferior.


### Matrizes de Confusão

As matrizes de confusão (calculadas para a classe-alvo de cada vídeo) ajudam a visualizar a contagem de Verdadeiros Positivos (TP), Falsos Positivos (FP) e Falsos Negativos (FN) em nível de frame.

**Smartwatch: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/095b3346-106e-43bb-84e2-158cb512db24" />

**Smartwatch: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/82deadcf-5c4d-4fc4-9688-fcf8ce100f40" />

As matrizes de confusão expõem o problema central da baixa Precisão. Em ambas as imagens, o quadrante 'Falso Positivo (FP)' (1686 e 1459) é massivo, sendo maior até que o de 'Verdadeiro Positivo (TP)' (1343 e 1105). Isso confirma que ambos os modelos erraram mais do que acertaram quando decidiram "ver" o smartwatch.

A vitória do 'General' é explicada pela diferença nos Falsos Negativos (FN): ele falhou em ver o objeto em apenas 199 frames, enquanto o 'Geral' falhou em 437 frames. O 'Especialista' foi mais sensível (alto Recall), mas pagou o preço com o maior número de Falsos Positivos.

--------------------------------------------------------------------------

**2. Blender (liquidificador):**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Geral | 0.120 | 0.700 | 0.065|
| Especialista | 0.157 | 0.617 | 0.090 |

**Análise:**
Para a classe 'Blender', o modelo 'Especialista' (F1=0.157) superou por uma pequena margem o 'Geral' (F1=0.120). No entanto, ambos os modelos apresentaram um desempenho geral muito baixo.
O ponto de falha catastrófico para ambos foi o Recall (Sensibilidade), com o 'Geral' registrando apenas 6,5% e o 'Especialista' 9,0%. Isso indica que ambos os modelos são efetivamente "cegos" para a classe 'Blender', falhando em detectá-la em mais de 90% dos frames em que ela estava presente (Falsos Negativos).

Notavelmente, o modelo 'Geral' teve uma Precisão alta (70,0%), sugerindo que nas raras ocasiões em que ele conseguiu fazer uma detecção, ele estava correto na maioria das vezes, gerando poucos Falsos Positivos.

### Análise Qualitativa

Os gráficos de linha do tempo mostram *quando* cada modelo acertou, errou ou se confundiu com outra classe. As cores representam a classe detectada em cada frame.

**Blender: Linha do Tempo Categórica**

<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/03851adb-266e-45bd-b782-ad233d5ab9e8" />


**Análise:** O gráfico acima expõe de forma dramática as diferentes falhas dos modelos. A linha do Ground_Truth (mais acima, roxa) está ativa durante a maior parte do vídeo.

A linha do 'Geral' (baixo) é um caos de detecções incorretas. Ela quase nunca acerta (roxo), validando seu péssimo Recall de 6,5%. Em vez disso, o modelo está "hiperativo", detectando erroneamente todas as outras classes (Smartwatch, Hair Dryer, Mixer, Grain Grinder) em sequência.

A linha do 'Especilaista' (meio) é o oposto: ela é extremamente esparsa. Ela consiste em "buracos" brancos (Falsos Negativos) com raras detecções corretas (roxo), o que explica seu Recall de 9,0%.

Em suma: o 'Geral' não é "cego", ele é "confuso", vendo objetos onde não há. O 'Especialista' é simplesmente "cego", não vendo quase nada.


### Matrizes de Confusão

As matrizes de confusão (calculadas para a classe-alvo de cada vídeo) ajudam a visualizar a contagem de Verdadeiros Positivos (TP), Falsos Positivos (FP) e Falsos Negativos (FN) em nível de frame.

**Smartwatch: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/96af056b-baaa-4ddb-9c83-cc4e06f5ccdc" />

**Blender: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/c300953a-4e10-4a59-aa73-3857947f48d2" />

As matrizes de confusão validam visualmente o colapso do Recall. Em ambas as imagens, o quadrante 'Falso Negativo (FN)' (2127 e 2071 frames) é expressivo, dominando completamente o quadrante 'Verdadeiro Positivo (TP)' (149 e 205 frames). Isso mostra que para cada detecção correta, os modelos falharam em ver o objeto mais de 10 vezes.

A alta Precisão é explicada pelos valores baixos de 'Falso Positivo (FP)' (64 e 127) em relação aos TPs. É um exemplo clássico de "paradoxo da precisão": o modelo quase nunca detecta o 'Blender', mas nas poucas vezes que detecta (TP+FP), ele tem uma chance razoável de estar certo (TP).

--------------------------------------------------------------------------

**3. Hair Dryer (Secador de Cabelo):**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Geral | 0.765 | 0.937 | 0.647|
| Especialista | 0.787 | 0.976 | 0.659 |

**Análise:**
Para a classe 'Hair Dryer', ambos os modelos apresentaram um desempenho forte e muito similar, com o 'Especialista' (F1=0.787) superando por uma margem muito pequena o 'Geral' (F1=0.765).

A característica marcante desta classe foi a Precisão (Precision) extraordinariamente alta para ambos os modelos (93,7% e 97,6%). Isso indica que, quando um dos modelos afirmava ter visto o secador de cabelo, ele estava quase sempre correto, gerando pouquíssimos Falsos Positivos.

### Análise Qualitativa

Os gráficos de linha do tempo mostram *quando* cada modelo acertou, errou ou se confundiu com outra classe. As cores representam a classe detectada em cada frame.

**Hair Dryer: Linha do Tempo Categórica**

<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/5be3dcb5-cf10-4b79-b41d-e9c205f0db8a" />


**Análise:** O gráfico acima ilustra as personalidades dos dois modelos. A linha do Ground_Truth (topo, vermelha) está ativa na maior parte do tempo.

A linha do 'Especialista' (meio) é muito "limpa": ela consiste quase exclusivamente de detecções corretas (vermelho), o que valida sua precisão de 97,6%. No entanto, ela possui vários "buracos" brancos (Falsos Negativos) que correspondem aos períodos em que o Ground Truth estava ativo, explicando seu Recall de 65,9%.

A linha do 'Geral' (baixo) é visivelmente mais "ruidosa", especialmente nos primeiros 40 segundos. Ela mostra várias detecções incorretas de Mixer (verde) e Smartwatch (azul), que são Falsos Positivos e explicam sua precisão ligeiramente menor (93,7%).

### Matrizes de Confusão

**Hair Dryer: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/2cb3088a-1640-42d6-be95-9b4e823c855d" />



**Hair Dryer: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/3f048582-8ca3-4fe2-8a48-7a6803b61ed7" />


As matrizes de confusão validam perfeitamente a análise quantitativa. A alta precisão de ambos os modelos é confirmada visualmente pelos valores baixíssimos no quadrante 'Falso Positivo (FP)' (apenas 91 frames para o 'Geral' e 34 frames para o 'Especialista') em relação ao total de frames analisados (~3600).

O Recall moderado também é evidente nos valores significativos do quadrante 'Falso Negativo (FN)' (740 e 715 frames, respectivamente). Isso mostra que, embora os modelos raramente tenham errado (FP), eles frequentemente falharam em ver (FN) o objeto que estava presente. O modelo 'Especialista' se destaca por ter o menor número de Falsos Positivos (34), o que explica sua Precisão quase perfeita de 97,6%.

--------------------------------------------------------------------------

**4. Mixer:**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Geral | 0.768 | 0.770 | 0.767|
| Especialista | 0.433 | 0.724 | 0.309 |

**Análise:**
Para a classe 'Mixer', o modelo 'Geral' (F1=0.768) foi o vencedor indiscutível, superando amplamente o modelo 'Especialista' (F1=0.433). A diferença de performance é explicada quase inteiramente pelo Recall (Sensibilidade).

O 'Geral' foi capaz de encontrar o 'Mixer' em 76,7% dos frames em que ele estava presente. Em contrapartida, o 'Geral' sofreu um colapso de sensibilidade, com um Recall de apenas 30,9%, falhando em detectar o objeto na maior parte do vídeo. A Precisão de ambos foi boa (77% e 72%), indicando que, quando faziam uma detecção, ela era majoritariamente correta.

### Análise Qualitativa

**Mixer: Linha do Tempo Categórica**

<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/d8dad6dc-0043-415e-9515-d4f1ed78e160" />


**Análise:** O gráfico acima ilustra perfeitamente a disparidade de Recall. A linha do Ground_Truth (topo, verde) está ativa durante quase todo o vídeo. A linha do 'Geral' (baixo) espelha de perto o Ground Truth, mostrando longos blocos de detecção correta (verde), validando seu alto Recall de 76,7%. Em contraste, a linha do 'Especialista' (meio) é composta por pequenos fragmentos, com vastos "buracos" brancos (Falsos Negativos) que correspondem ao seu péssimo Recall de 30,9%. O gráfico também expõe a confusão do 'Geral', que, apesar de bom, ocasionalmente detecta Smartwatch (azul) ou Hair Dryer (vermelho) no lugar do mixer.

### Matrizes de Confusão

**Mixer: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/6d393fde-4c25-49e3-bc4d-9a073898bd20" />


**Mixer: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/d53a80e1-95ed-41e3-95e0-4a127c1561a4" />


As matrizes de confusão confirmam a análise quantitativa. A matriz do modelo 'Especialista' mostra um desequilíbrio extremo, com o número de Falsos Negativos (FN) (1253 frames) sendo mais que o dobro dos Verdadeiros Positivos (TP) (561 frames), o que valida o seu baixíssimo Recall. Em contrapartida, a matriz do 'Geral' é muito mais equilibrada, com um alto número de TP (1391) em relação aos FN (423). O quadrante Falso Positivo (FP) do 'Geral' (416 frames) é o que limita sua Precisão a 77%.

--------------------------------------------------------------------------

**5. Grain Grinder (Moedor de Grãos):**

| Model | F1-Score | Precision | Recall |
| :--- | ---: | ---: | ---: |
| Geral | 0.628 | 0.672 | 0.590|
| Especialista | 0.443 | 0.593 | 0.353 |

**Análise:**
Para a classe 'Grain Grinder', o modelo 'geral' (F1=0.628) obteve um desempenho significativamente superior ao do 'Especialista' (F1=0.443). Assim como na classe 'Mixer', a principal causa da disparidade foi o Recall (Sensibilidade).

O 'Geral' conseguiu encontrar o 'Grain Grinder' em 59,0% dos frames em que ele estava visível, enquanto o 'Especialista' teve uma performance muito fraca, com um Recall de apenas 35,3%. Ambos os modelos tiveram uma Precisão (Precision) moderada (67,2% e 59,3%), indicando que ambos geraram um número considerável de Falsos Positivos.

### Análise Qualitativa

**Grain Grinder: Linha do Tempo Categórica**

<img width="1990" height="490" alt="image" src="https://github.com/user-attachments/assets/df9a74ff-1394-483d-8728-e24e8427cb67" />



**Análise:** O gráfico acima expõe a "confusão" de ambos os modelos. A linha do Ground_Truth (topo, laranja) mostra que o objeto está presente em grandes blocos. A linha do 'Geral' (baixo) é extremamente ruidosa; embora capture corretamente o 'Grain Grinder' (laranja) em vários momentos (explicando seu Recall de 59%), ela está contaminada por detecções incorretas de Smartwatch (azul) e Mixer (verde), o que justifica sua Precisão de apenas 67%. A linha do 'Especialista' (meio) é muito mais esparsa, com longos "buracos" brancos (Falsos Negativos) que validam seu baixo Recall de 35%.

### Matrizes de Confusão

**Grain Grinder: Matriz de Confusão (Modelo Especialista vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/d6dadfc0-cfe2-4811-ace8-34c40cb37dc8" />

**Grain Grinder: Matriz de Confusão (Modelo Geral vs. Classe-Alvo)**

<img width="395" height="295" alt="image" src="https://github.com/user-attachments/assets/8aa969d8-0fc9-42c6-877b-e063c1e9f745" />


As matrizes confirmam a análise. A matriz do 'Especialista' (Detecção, primeira imagem) mostra que o número de Falsos Negativos (FN) (986 frames) é quase o dobro do de Verdadeiros Positivos (TP) (538 frames), explicando o colapso do Recall.

Em contraste, a matriz do 'Geral' (Classificação, segunda imagem) é muito mais equilibrada, com TP (899 frames) superando os FN (625 frames), o que valida seu Recall superior. O alto número de Falsos Positivos (FP) (439 frames) nesta matriz é a causa da sua Precisão moderada e do "ruído" visual visto no gráfico de linha do tempo.

## Como Replicar o Experimento

Este repositório está estruturado para permitir a replicação completa da análise. Para isso serão necessáriuos alguns ajustes e configurações nos caminhos dos arquivos. Você pode iniciar o experimento desde a etapa de treino dos modelos. As cinco classes da bse VERD encontram-se no repositório, no diretório [Videos](https://github.com/rafaeljbi/Granular_Video/tree/main/No_Annotation/Videos).

A descrição das classes encontra-se no arquivo [Class_Identification.txt](https://github.com/rafaeljbi/Granular_Video/blob/main/Other/Class_Identification.txt).

O script de **extração dos frames** e **treinamnto do modelo 'Geral' (sem os bounding boxes)** foi feito pelo Google collab no notebook [Extract_and_Train.ipynb](https://github.com/rafaeljbi/Granular_Video/blob/main/No_Annotation/Extract_and_Train.ipynb). Para usá-lo localemente será necessário configurar os diretóios de extração e salvamento do modelo. Os frames extraídos (usados posteriormente para anotação no roboflow) encontram-se no diiretório [Frames_extract](https://github.com/rafaeljbi/Granular_Video/tree/main/No_Annotation/Frames_extract).

A base anotada pelo roboflow (com os bounding boxes) encontra-se em **Base_roboflow**.

O Script para treino do modelo 'Especialista' é o arquivo [Training_VERD_Roboflow3.ipynb](https://github.com/rafaeljbi/Granular_Video/blob/main/With_annotation/Training_VERD_Roboflow3.ipynb).

