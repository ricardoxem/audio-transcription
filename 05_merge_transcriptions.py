import os
from dotenv import load_dotenv

def run() -> str:
    """Etapa 05: une as transcrições em um único arquivo final."""
    # === Carregar variáveis do .env ===
    load_dotenv()

    input_dir = os.getenv("DIR_TRANSCRIPTIONS")
    output_dir = os.getenv("DIR_FINAL_TRANSCRIPTION")
    input_audio_path = os.getenv("INPUT_AUDIO_AAC")

    if not input_dir:
        raise ValueError("Variável de ambiente não definida: DIR_TRANSCRIPTIONS")
    if not output_dir:
        raise ValueError("Variável de ambiente não definida: DIR_FINAL_TRANSCRIPTION")
    if not input_audio_path:
        raise ValueError("Variável de ambiente não definida: INPUT_AUDIO_AAC")

    base_name = os.path.splitext(os.path.basename(input_audio_path))[0]
    output_file_path = os.path.join(output_dir, f"{base_name}_transcricao_completa.txt")

    # === Criar diretório de saída, se necessário ===
    os.makedirs(output_dir, exist_ok=True)

    # === Listar e ordenar os arquivos de transcrição ===
    transcription_files = sorted(
        [f for f in os.listdir(input_dir) if f.lower().endswith(".txt")]
    )

    print("🧩 Unindo arquivos de transcrição...")

    with open(output_file_path, "w", encoding="utf-8") as outfile:
        for fname in transcription_files:
            file_path = os.path.join(input_dir, fname)
            print(f"📄 Incluindo: {fname}")
            with open(file_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # separador entre arquivos

    print(f"\n✅ Arquivo final salvo em: {output_file_path}")
    return output_file_path


if __name__ == "__main__":
    run()
