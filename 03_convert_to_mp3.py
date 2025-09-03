import os
from pydub import AudioSegment
from dotenv import load_dotenv

# === Carregar variáveis do .env ===
load_dotenv()

INPUT_DIR = os.getenv("DIR_CHUNKS_VOLUME_ADJUSTED_AAC")
OUTPUT_DIR = os.getenv("DIR_CHUNKS_MP3")

# === Criar diretório de saída, se não existir ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🎧 Convertendo chunks ajustados para MP3...")

for filename in sorted(os.listdir(INPUT_DIR)):
    if not filename.lower().endswith(".m4a"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")

    print(f"🎵 Convertendo: {filename} → {base_name}.mp3")

    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3", bitrate="192k")

print("\n✅ Conversão finalizada.")
