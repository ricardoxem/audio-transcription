import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel

def run() -> int:
    """Etapa 04: transcreve os chunks MP3 com Faster-Whisper."""
    # === Carregar variáveis do .env ===
    load_dotenv()

    input_dir = os.getenv("DIR_CHUNKS_MP3")
    output_dir = os.getenv("DIR_TRANSCRIPTIONS")
    model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")
    language = os.getenv("WHISPER_MODEL_LANG", "pt")

    if not input_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_MP3")
    if not output_dir:
        raise ValueError("Variável de ambiente não definida: DIR_TRANSCRIPTIONS")

    # === Criar diretório de saída, se não existir ===
    os.makedirs(output_dir, exist_ok=True)

    print(f"🧠 Carregando modelo Whisper ({model_size})...")
    model = WhisperModel(model_size, compute_type="int8")

    print("✍️ Transcrevendo chunks MP3...")

    # Offset global em segundos (para este áudio/processamento)
    time_offset = 0.0
    transcribed = 0

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".mp3"):
            continue

        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        print(f"🗂️ Transcrevendo: {filename}")

        segments, info = model.transcribe(input_path, language=language)

        with open(output_path, "w", encoding="utf-8") as f:
            for segment in segments:
                # Corrige os tempos somando o offset acumulado
                start = round(segment.start + time_offset, 2)
                end = round(segment.end + time_offset, 2)
                text = segment.text.strip()
                f.write(f"[{start}s - {end}s] {text}\n")

        # Atualiza o offset para o próximo chunk
        time_offset += info.duration  # duração real do áudio processado
        transcribed += 1

    print("\n✅ Transcrição concluída.")
    return transcribed


if __name__ == "__main__":
    run()
