import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel

# === Carregar variáveis do .env ===
load_dotenv()

INPUT_DIR = os.getenv("DIR_CHUNKS_MP3")
OUTPUT_DIR = os.getenv("DIR_TRANSCRIPTIONS")
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "medium")
LANGUAGE = os.getenv("WHISPER_MODEL_LANG", "pt")

# === Criar diretório de saída, se não existir ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🧠 Carregando modelo Whisper ({MODEL_SIZE})...")
model = WhisperModel(MODEL_SIZE, compute_type="int8")

print("✍️ Transcrevendo chunks MP3...")

# Offset global em segundos
time_offset = 0.0

for filename in sorted(os.listdir(INPUT_DIR)):
    if not filename.lower().endswith(".mp3"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")

    print(f"🗂️ Transcrevendo: {filename}")

    segments, info = model.transcribe(input_path, language=LANGUAGE)

    with open(output_path, "w", encoding="utf-8") as f:
        for segment in segments:
            # Corrige os tempos somando o offset acumulado
            start = round(segment.start + time_offset, 2)
            end = round(segment.end + time_offset, 2)
            text = segment.text.strip()
            f.write(f"[{start}s - {end}s] {text}\n")

    # Atualiza o offset para o próximo chunk
    time_offset += info.duration  # duração real do áudio processado

print("\n✅ Transcrição concluída.")
