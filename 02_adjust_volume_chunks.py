import os
import subprocess
from pydub import AudioSegment
from dotenv import load_dotenv

def get_mean_volume_db(filepath):
    """Usa FFmpeg para calcular o volume médio do arquivo."""
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "volumedetect",
        "-f", "null", "/dev/null"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.splitlines():
        if "mean_volume:" in line:
            try:
                return float(line.strip().split(":")[1].replace(" dB", "").strip())
            except ValueError:
                pass
    return None

def run() -> int:
    """Etapa 02: ajusta o volume dos chunks (.m4a) usando thresholds."""
    # === Carregar variáveis do .env ===
    load_dotenv()

    input_dir = os.getenv("DIR_CHUNKS_ORIGINAL_AAC")
    output_dir = os.getenv("DIR_CHUNKS_VOLUME_ADJUSTED_AAC")
    volume_threshold_db = float(os.getenv("VOLUME_THRESHOLD_DB", -25))
    volume_target_db = float(os.getenv("VOLUME_TARGET_DB", -18))
    volume_max_gain_db = float(os.getenv("VOLUME_MAX_GAIN_DB", 20))

    if not input_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_ORIGINAL_AAC")
    if not output_dir:
        raise ValueError("Variável de ambiente não definida: DIR_CHUNKS_VOLUME_ADJUSTED_AAC")

    # === Criar diretório de saída, se não existir ===
    os.makedirs(output_dir, exist_ok=True)

    print("📊 Ajustando volume dos chunks...")
    processed = 0

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".m4a"):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"\n🔍 Processando: {filename}")
        mean_volume = get_mean_volume_db(input_path)

        if mean_volume is None:
            print("⚠️  Não foi possível detectar o volume.")
            continue

        print(f"🎚️  Volume médio detectado: {mean_volume:.2f} dB")

        if mean_volume < volume_threshold_db:
            gain = min(volume_target_db - mean_volume, volume_max_gain_db)
            print(f"🔊 Aumentando volume em {gain:.2f} dB")
            audio = AudioSegment.from_file(input_path)
            louder = audio + gain
            louder.export(output_path, format="ipod")  # 'ipod' = m4a/AAC
        elif mean_volume > -3:  # evita clipping
            reduction = min(mean_volume - volume_target_db, volume_max_gain_db)
            print(f"🔉 Diminuindo volume em {reduction:.2f} dB")
            audio = AudioSegment.from_file(input_path)
            quieter = audio - reduction
            quieter.export(output_path, format="ipod")
        else:
            print("✅ Volume aceitável. Copiando sem alterações.")
            AudioSegment.from_file(input_path).export(output_path, format="ipod")

        processed += 1

    print("\n✅ Ajuste de volume finalizado.")
    return processed


if __name__ == "__main__":
    run()
