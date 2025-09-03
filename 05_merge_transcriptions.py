import os
from dotenv import load_dotenv

# === Carregar variáveis do .env ===
load_dotenv()

INPUT_DIR = os.getenv("DIR_TRANSCRIPTIONS")
OUTPUT_DIR = os.getenv("DIR_FINAL_TRANSCRIPTION")
INPUT_AUDIO_PATH = os.getenv("INPUT_AUDIO_AAC")
base_name = os.path.splitext(os.path.basename(INPUT_AUDIO_PATH))[0]
output_file_path = os.path.join(OUTPUT_DIR, f"{base_name}_transcricao_completa.txt")

# === Criar diretório de saída, se necessário ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Listar e ordenar os arquivos de transcrição ===
transcription_files = sorted([
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(".txt")
])

print("🧩 Unindo arquivos de transcrição...")

with open(output_file_path, "w", encoding="utf-8") as outfile:
    for fname in transcription_files:
        file_path = os.path.join(INPUT_DIR, fname)
        print(f"📄 Incluindo: {fname}")
        with open(file_path, "r", encoding="utf-8") as infile:
            outfile.write(infile.read())
            outfile.write("\n")  # separador entre arquivos

print(f"\n✅ Arquivo final salvo em: {output_file_path}")
