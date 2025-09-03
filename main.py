import os
from pydub import AudioSegment
from faster_whisper import WhisperModel

# === Configurações ===
PART_DURATION_SECONDS = 900  # 15 minutos
MODEL_SIZE = "large-v2"
LANGUAGE = "pt"

# === Entrada do usuário ===
audio_path = "input/Tânia.aac"
if not os.path.isfile(audio_path):
    raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")

# === Diretórios de saída ===
output_dir_chunks = "output_transcricao"
output_dir_full = "output_transcricao_completa"
os.makedirs(output_dir_chunks, exist_ok=True)
os.makedirs(output_dir_full, exist_ok=True)

# Nome base e caminhos
base_name = os.path.splitext(os.path.basename(audio_path))[0]
output_file = os.path.join(output_dir_full, f"{base_name}_transcricao_completa.txt")

# === Carregar áudio ===
print("🔍 Carregando áudio...")
audio = AudioSegment.from_file(audio_path)
audio_duration = len(audio) / 1000  # em segundos

# === Quebrar em partes, se necessário ===
parts = []
if audio_duration > PART_DURATION_SECONDS:
    print(f"🔪 Quebrando áudio em partes de {PART_DURATION_SECONDS} segundos...")
    for i, start in enumerate(range(0, int(audio_duration), PART_DURATION_SECONDS)):
        end = min(start + PART_DURATION_SECONDS, int(audio_duration))
        chunk = audio[start * 1000:end * 1000]
        chunk_path = os.path.join(output_dir_chunks, f"{base_name}_chunk_{i}.mp3")
        chunk.export(chunk_path, format="mp3")
        parts.append((chunk_path, start))
else:
    parts.append((audio_path, 0))

# === Carregar modelo ===
print(f"🧠 Carregando modelo Whisper ({MODEL_SIZE})...")
model = WhisperModel(MODEL_SIZE, compute_type="int8")

# === Transcrever e salvar ===
print("📝 Iniciando transcrição...\n")
with open(output_file, "w", encoding="utf-8") as full_out:
    for i, (part_path, offset) in enumerate(parts):
        print(f"🎙️ Transcrevendo parte {i + 1}/{len(parts)}: {os.path.basename(part_path)}")

        segments, _ = model.transcribe(part_path, language=LANGUAGE)

        # Salvar transcrição da parte individual
        part_transcription_path = os.path.join(output_dir_chunks, f"{base_name}_chunk_{i}_transcricao.txt")
        with open(part_transcription_path, "w", encoding="utf-8") as part_out:
            for segment in segments:
                start = round(segment.start + offset, 2)
                end = round(segment.end + offset, 2)
                text = segment.text.strip()
                line = f"[{start}s - {end}s] {text}"
                part_out.write(line + "\n")
                full_out.write(line + "\n")

        # Remover chunk se ele foi criado temporariamente
        if not part_path.endswith(".aac"):
            os.remove(part_path)
            print(f"🧹 Removido arquivo temporário: {os.path.basename(part_path)}")

print(f"\n✅ Transcrição final salva em: {output_file}")
