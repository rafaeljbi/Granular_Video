#Esse script será usado para anotar os dados reais nosvídeos coletados.


#Para essa etapa de anotação, será necessário desinstalar o openCV headless# 
# pip uninstall opencv-python-headless
#e instalar:
#pip install opencv-python

import cv2
import csv
import os

# --- Configuração ---

# 1. Pasta onde estão seus vídeos de 2 minutos
VIDEO_FOLDER = "D:/Tese_UPM/Granular_Recognition/Projetos/Granular_Video/Comparison/Videos_comparison" # (a pasta do script anterior)

# 2. Arquivo de saída para suas anotações
OUTPUT_LOG = "D:/Tese_UPM/Granular_Recognition/Projetos/Granular_Video/Comparison/log_ground_truth.txt"

# 3. Mapeamento das Teclas para as Classes
#    (Ajuste as teclas como preferir)
CLASS_KEYS = {
    '1': 'Smartwatch',
    '2': 'Hair_Dryer',
    '3': 'Mixer',
    '4': 'Grain_grinder',
    '5': 'Blender'
}
# --- Fim da Configuração ---


print("--- Anotador Manual de Ground Truth ---")
print(f"Salvando anotações em: {OUTPUT_LOG}")
print("\nInstruções:")
for key, name in CLASS_KEYS.items():
    print(f" Pressione '{key}' para anotar -> {name}")
print(" Pressione [ESPAÇO] para PAUSAR / DESPAUSAR.")
print(" Pressione [Q] para PULAR para o próximo vídeo.")
print("------------------------------------------")

# Pega todos os vídeos na pasta
try:
    videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith('.mp4')]
    if not videos:
        print(f"Erro: Nenhum vídeo .mp4 encontrado na pasta '{VIDEO_FOLDER}'")
        exit()
except FileNotFoundError:
    print(f"Erro: Pasta não encontrada: '{VIDEO_FOLDER}'")
    exit()

# Abre o arquivo de log para escrever (modo 'w' = apaga o anterior)
with open(OUTPUT_LOG, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Escreve o cabeçalho
    writer.writerow(["Timestamp_Video_s", "Anotador", "Classe"])

    # Loop por cada vídeo na pasta
    for video_file in sorted(videos):
        video_path = os.path.join(VIDEO_FOLDER, video_file)
        print(f"\nCarregando vídeo: {video_file}...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"  Erro ao abrir {video_file}.")
            continue

        # Pega o FPS para o vídeo tocar na velocidade correta
        fps = cap.get(cv2.CAP_PROP_FPS)
        # O delay entre os frames é 1000ms / FPS
        # (usamos max(1, ...) para evitar delay 0)
        delay = int(1000 / fps) 

        # Loop principal do vídeo
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break # Fim do vídeo

            # Pega o timestamp ATUAL em segundos
            timestamp_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            # Escreve o timestamp no vídeo
            cv2.putText(
                frame, 
                f'Tempo: {timestamp_s:.2f}s', 
                (10, 30), # Posição (x, y)
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, # Tamanho da fonte
                (0, 255, 0), # Cor (Verde)
                2 # Espessura
            )
            
            # Mostra o frame
            window_name = f'Anotando: {video_file} - (Q para pular)'
            cv2.imshow(window_name, frame)

            # Espera pela tecla (com o delay correto do FPS)
            key_code = cv2.waitKey(delay)
            
            # --- Lógica das Teclas ---

            # 1. 'q' para Sair/Pular
            if key_code == ord('q'):
                print("  Vídeo pulado pelo usuário.")
                break

            # 2. 'Espaço' para Pausar
            if key_code == ord(' '):
                print(f"  PAUSADO em {timestamp_s:.2f}s. Pressione qualquer tecla para continuar...")
                cv2.waitKey(0) # Espera indefinidamente por uma tecla

            # 3. Teclas de Anotação
            key_char = chr(key_code & 0xFF)
            if key_char in CLASS_KEYS:
                class_name = CLASS_KEYS[key_char]
                
                # Prepara os dados para salvar
                log_data = [f"{timestamp_s:.4f}", "Manual", class_name]
                
                # Salva no arquivo
                writer.writerow(log_data)
                
                # Imprime no console
                print(f"  Anotado: {log_data[0]}s  -> {log_data[2]}")

        # Fim do loop do vídeo, limpa
        cap.release()

    # Fim de todos os vídeos
    cv2.destroyAllWindows()
    print("\n--- Anotação Manual Concluída! ---")
    print(f"Seu Ground Truth foi salvo em: {OUTPUT_LOG}")