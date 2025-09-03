# 01_split_audio_chunks.py

import os
from pydub import AudioSegment
from dotenv import load_dotenv

# === Carregar variáveis de ambiente ===
load_dotenv()

INPUT_AUDIO = os.getenv("INPUT_AUDIO_AAC")
OUTPUT_DIR = os.getenv("DIR_CHUNKS_ORIGINAL_AAC")
CHUNK_DURATION_SECONDS = int(os.getenv("CHUNK_DURATION_SECONDS"))

# === Verificações iniciais ===
if not os.path.isfile(INPUT_AUDIO):
    raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_AUDIO}")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Carregar áudio ===
print("🔪 Quebrando áudio em chunks...")
audio = AudioSegment.from_file(INPUT_AUDIO)
audio_length_ms = len(audio)

# === Dividir em chunks ===
chunks = []
for i, start_ms in enumerate(range(0, audio_length_ms, CHUNK_DURATION_SECONDS * 1000)):
    end_ms = min(start_ms + CHUNK_DURATION_SECONDS * 1000, audio_length_ms)
    chunk = audio[start_ms:end_ms]

    # Gerar nome do arquivo de chunk
    chunk_path = os.path.join(OUTPUT_DIR, f"chunk_{i:03}.m4a")
    chunk.export(chunk_path, format="mp4")  # usa contêiner mp4 (m4a)

    print(f"✅ Chunk {i} salvo: {chunk_path}")
    chunks.append(chunk_path)

print(f"\n📂 Total de chunks gerados: {len(chunks)}")
