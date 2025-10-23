#It is important to have all libraries installed. 
#To install the following library on your terminal: 
#pip install yt-dlp

import cv2
import csv
import torch
from ultralytics import YOLO
import yt_dlp
from datetime import datetime
import time


# --- Configuração ---
YOUTUBE_URL = "https://www.youtube.com/watch?v=P3rPEoy82Uk" #Add the URL you want to analyze here
OUTPUT_FILE = "D:/Tese_UPM/In_the_wild_test/log_Hainr_dryer.txt" #Output path
CONFIDENCE_THRESHOLD = 0.6 # Adjust the confidence of the models

# --- Limite de tempo ---
MAX_PROCESS_TIME_SECONDS = 120 # usado para limitr o tempo de análise do vídeo

# Dicionário de mapeamento para os nomes das classes
CLASS_NAME_MAPPING = {
    "50000262": "Smartwatch",
    "50001708": "Grain_grinder",
    "50001726_2": "Mixer",
    "50001861": "Blender",
    "50001986": "Hair_Dryer"
}

# Mapeie os nomes dos seus modelos para os nomes que você quer no log
MODELOS = {
    "Especialista": YOLO("D:/Tese_UPM/Testes_YoloV8/best3_no_annotation.pt"),#replace with your model path
    "Geral": YOLO("D:/Tese_UPM/Testes_YoloV8/best4_with_annotation.pt")#replace with your model path
}
# --- Fim da Configuração ---
print(f"Processando vídeo: {YOUTUBE_URL}")
print("Acessando stream do YouTube com yt-dlp...")

try:
    YDL_OPTS = {
        'format': 'best[ext=mp4][vcodec^=avc]/best[ext=mp4]/best',
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
        stream_url = info_dict.get('url', None)
        video_title = info_dict.get('title', 'No Title')

    if not stream_url:
        raise ValueError("Não foi possível obter a URL do stream com yt-dlp.")

    print(f"Stream URL obtida. Título: {video_title}")

except Exception as e:
    print(f"Erro ao acessar o stream do YouTube com yt-dlp: {e}")
    exit()


cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Erro: Não foi possível abrir o stream de vídeo.")
    exit()

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp_Video_s", "Modelo", "Classe", "Confianca"])
    
    print(f"Iniciando processamento frame a frame (limite de {MAX_PROCESS_TIME_SECONDS} segundos)...")
    print("Isso pode demorar. Pressione Ctrl+C no terminal para parar.")

    frame_count = 0
    start_time = time.time()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Fim do vídeo ou erro de leitura.")
                break

            video_timestamp_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 
            log_timestamp = f"{video_timestamp_s:.4f}"

            # --- NOVO: Verificação do Limite de Tempo ---
            if video_timestamp_s > MAX_PROCESS_TIME_SECONDS:
                print(f"\nLimite de {MAX_PROCESS_TIME_SECONDS} segundos de vídeo atingido.")
                break
            # --- Fim da Verificação ---

            # Processa o frame com cada modelo
            for model_name, model in MODELOS.items():
                
                results = model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)
                
                # Se for um modelo de DETECÇÃO (com bounding box)
                if results[0].boxes:
                    for box in results[0].boxes:
                        conf = box.conf.item()
                        cls_id = box.cls.item()
                        class_name = model.names[int(cls_id)]
                        
                        if model_name == "Especialista" and class_name in CLASS_NAME_MAPPING:
                            class_name = CLASS_NAME_MAPPING[class_name]
                        
                        writer.writerow([log_timestamp, model_name, class_name, f"{conf:.4f}"])

                # Se for um modelo de CLASSIFICAÇÃO (sem bounding box)
                elif results[0].probs:
                    conf = results[0].probs.top1conf.item()
                    if conf >= CONFIDENCE_THRESHOLD:
                        cls_id = results[0].probs.top1
                        class_name = model.names[int(cls_id)]
                        
                        if model_name == "Especialista" and class_name in CLASS_NAME_MAPPING:
                            class_name = CLASS_NAME_MAPPING[class_name]

                        writer.writerow([log_timestamp, model_name, class_name, f"{conf:.4f}"])

            
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"Processando... Frame {frame_count} (Timestamp: {log_timestamp}s)")

    except KeyboardInterrupt:
        print("Processamento interrompido pelo usuário (Ctrl+C).")
    
    finally:
        # Fecha tudo
        cap.release()
        end_time = time.time()
        print(f"\nProcessamento concluído.")
        print(f"Arquivo de log salvo em: {OUTPUT_FILE}")
        print(f"Total de frames processados: {frame_count}")
        print(f"Tempo total de processamento: {end_time - start_time:.2f} segundos")