import os
import subprocess
from pydub import AudioSegment
from dotenv import load_dotenv

# === Carregar variáveis do .env ===
load_dotenv()

INPUT_DIR = os.getenv("DIR_CHUNKS_ORIGINAL_AAC")
OUTPUT_DIR = os.getenv("DIR_CHUNKS_VOLUME_ADJUSTED_AAC")
VOLUME_THRESHOLD_DB = float(os.getenv("VOLUME_THRESHOLD_DB", -25))
VOLUME_TARGET_DB = float(os.getenv("VOLUME_TARGET_DB", -18))
VOLUME_MAX_GAIN_DB = float(os.getenv("VOLUME_MAX_GAIN_DB", 20))

# === Criar diretório de saída, se não existir ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

print("📊 Ajustando volume dos chunks...")

for filename in sorted(os.listdir(INPUT_DIR)):
    if not filename.lower().endswith(".m4a"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"\n🔍 Processando: {filename}")
    mean_volume = get_mean_volume_db(input_path)

    if mean_volume is None:
        print("⚠️  Não foi possível detectar o volume.")
        continue

    print(f"🎚️  Volume médio detectado: {mean_volume:.2f} dB")

    if mean_volume < VOLUME_THRESHOLD_DB:
        gain = min(VOLUME_TARGET_DB - mean_volume, VOLUME_MAX_GAIN_DB)
        print(f"🔊 Aumentando volume em {gain:.2f} dB")
        audio = AudioSegment.from_file(input_path)
        louder = audio + gain
        louder.export(output_path, format="ipod")  # 'ipod' = m4a/AAC
    elif mean_volume > -3:  # evita clipping
        reduction = min(mean_volume - VOLUME_TARGET_DB, VOLUME_MAX_GAIN_DB)
        print(f"🔉 Diminuindo volume em {reduction:.2f} dB")
        audio = AudioSegment.from_file(input_path)
        quieter = audio - reduction
        quieter.export(output_path, format="ipod")
    else:
        print("✅ Volume aceitável. Copiando sem alterações.")
        AudioSegment.from_file(input_path).export(output_path, format="ipod")

print("\n✅ Ajuste de volume finalizado.")
