import os
from pydub import AudioSegment
from dotenv import load_dotenv

def run() -> int:
    """Etapa 03: converte os chunks ajustados (.m4a) para MP3."""
    # === Carregar variáveis do .env ===
    load_dotenv()

    input_dir = os.getenv("DIR_CHUNKS_VOLUME_ADJUSTED_AAC")
    output_dir = os.getenv("DIR_CHUNKS_MP3")

    if not input_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_VOLUME_ADJUSTED_AAC")
    if not output_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_MP3")

    # === Criar diretório de saída, se não existir ===
    os.makedirs(output_dir, exist_ok=True)

    print("🎧 Convertendo chunks ajustados para MP3...")
    converted = 0

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".m4a"):
            continue

        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}.mp3")

        print(f"🎵 Convertendo: {filename} → {base_name}.mp3")

        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format="mp3", bitrate="192k")
        converted += 1

    print("\n✅ Conversão finalizada.")
    return converted


if __name__ == "__main__":
    run()
