#Run this on the terminal,  if necessary:
#Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
#then run this:
# choco install ffmpeg

import yt_dlp
import os

# --- Configuração ---

# 1. Dicionário com os vídeos
#    O nome antes dos ":" será o nome do arquivo
videos_para_baixar = {
    "Hair_Dryer": "https://www.youtube.com/watch?v=P3rPEoy82Uk",
    "Mixer": "https://www.youtube.com/watch?v=z7mW82k8Vp4",
    "Grain_grinder": "https://www.youtube.com/watch?v=ZeBEq7a2mgI",
    "Blender": "https://www.youtube.com/watch?v=M8B00ELaMtg",
    "Smartwatch": "https://www.youtube.com/watch?v=2w4EkcEH8jU" # O &t=330s será ignorado
}

# 2. Duração do corte em segundos
DURACAO_SEGUNDOS = 120 # 2 minutos

# 3. Pasta para salvar os vídeos
PASTA_SAIDA = "D:\Tese_UPM\Granular_Recognition\Projetos\Granular_Video\Comparison\Videos_comparison"

# --- Fim da Configuração ---

# Criar a pasta de saída se não existir
if not os.path.exists(PASTA_SAIDA):
    os.makedirs(PASTA_SAIDA)

print(f"Iniciando download dos primeiros {DURACAO_SEGUNDOS} segundos de cada vídeo...")
print(f"Os arquivos serão salvos na pasta: {PASTA_SAIDA}")

# Loop para baixar cada vídeo
for nome_base, url in videos_para_baixar.items():
    
    # Define o nome do arquivo final, ex: "videos_cortados/Smartwatch.mp4"
    nome_arquivo_final = os.path.join(PASTA_SAIDA, f"{nome_base}.mp4")
    
    print(f"\nProcessando: {nome_base} (de {url})")

    # Configurações do yt-dlp
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Pega o melhor formato mp4
        
        # --- A MÁGICA ACONTECE AQUI ---
        # 1. Diz ao yt-dlp para baixar apenas este intervalo de tempo.
        #    Requer 'ffmpeg' instalado no sistema!
        'download_ranges': yt_dlp.utils.download_range_func(None, [(0, DURACAO_SEGUNDOS)]),
        
        # 2. Força o uso do ffmpeg para cortar o início (mais preciso)
        'force_keyframes_at_cuts': True,
        
        # 3. Define o nome do arquivo de saída
        'outtmpl': nome_arquivo_final,
        
        # 4. Sobrescreve o arquivo se ele já existir
        'overwrites': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Sucesso: '{nome_arquivo_final}' salvo.")
        
    except Exception as e:
        print(f"--- ERRO ao baixar {nome_base} ---")
        
print("\nProcesso concluído.")