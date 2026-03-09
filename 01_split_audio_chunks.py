# 01_split_audio_chunks.py

import os
from pydub import AudioSegment
from dotenv import load_dotenv

def run(input_audio_path: str) -> list[str]:
    """Etapa 01: quebra o áudio AAC em chunks (.m4a)."""
    # === Carregar variáveis de ambiente ===
    load_dotenv()

    output_dir = os.getenv("DIR_CHUNKS_ORIGINAL_AAC")
    chunk_duration_raw = os.getenv("CHUNK_DURATION_SECONDS")

    if not output_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_ORIGINAL_AAC")
    if not chunk_duration_raw:
        raise ValueError("Variável de ambiente não definida: CHUNK_DURATION_SECONDS")

    # Aceita linhas tipo: "600  # 10min"
    chunk_duration_seconds = int(chunk_duration_raw.split("#", 1)[0].strip())

    # === Verificações iniciais ===
    if not os.path.isfile(input_audio_path):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_audio_path}")

    os.makedirs(output_dir, exist_ok=True)

    # === Carregar áudio ===
    print("🔪 Quebrando áudio em chunks...")
    audio = AudioSegment.from_file(input_audio_path)
    audio_length_ms = len(audio)

    # === Dividir em chunks ===
    chunks: list[str] = []
    for i, start_ms in enumerate(range(0, audio_length_ms, chunk_duration_seconds * 1000)):
        end_ms = min(start_ms + chunk_duration_seconds * 1000, audio_length_ms)
        chunk = audio[start_ms:end_ms]

        # Gerar nome do arquivo de chunk
        chunk_path = os.path.join(output_dir, f"chunk_{i:03}.m4a")
        chunk.export(chunk_path, format="mp4")  # usa contêiner mp4 (m4a)

        print(f"✅ Chunk {i} salvo: {chunk_path}")
        chunks.append(chunk_path)

    print(f"\n📂 Total de chunks gerados: {len(chunks)}")
    return chunks


if __name__ == "__main__":
    # Para uso standalone, ainda permite pegar do .env (mas o pipeline passa por parâmetro).
    load_dotenv()
    env_input = os.getenv("INPUT_AUDIO_AAC")
    if not env_input:
        raise SystemExit("Defina INPUT_AUDIO_AAC no .env ou use o run_pipeline.py")
    run(env_input)
