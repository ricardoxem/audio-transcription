"""
Roda o pipeline completo (etapas 01 -> 05) em sequência para TODOS os
arquivos dentro de `00_input_raw_audio/`.

Para cada arquivo:
- define `INPUT_AUDIO_AAC` automaticamente (sem precisar editar o .env)
- roda todas as etapas (01..05)
- limpa os diretórios intermediários ao final, mantendo a saída final

Uso:
  python run_pipeline.py
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import importlib

import clean_pipeline


def _run_step(module_name: str) -> object:
    mod = importlib.import_module(module_name)
    if not hasattr(mod, "run"):
        raise AttributeError(f"Módulo {module_name} não possui função run()")
    return mod.run()  # type: ignore[attr-defined]

def _run_step_01_split(input_audio_path: str) -> object:
    mod = importlib.import_module("01_split_audio_chunks")
    if not hasattr(mod, "run"):
        raise AttributeError("Módulo 01_split_audio_chunks não possui função run()")
    return mod.run(input_audio_path)  # type: ignore[attr-defined]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _set_default_envs(repo: Path) -> None:
    """
    Define defaults para variáveis que o pipeline precisa, caso não existam no .env.
    (As etapas chamam load_dotenv(), mas não sobrescrevem vars já definidas.)
    """
    os.environ.setdefault("DIR_CHUNKS_ORIGINAL_AAC", str(repo / "01_audio_chunks_original_aac"))
    os.environ.setdefault(
        "DIR_CHUNKS_VOLUME_ADJUSTED_AAC", str(repo / "02_audio_chunks_volume_adjusted_aac")
    )
    os.environ.setdefault("DIR_CHUNKS_MP3", str(repo / "03_audio_chunks_to_mp3"))
    os.environ.setdefault("DIR_TRANSCRIPTIONS", str(repo / "04_audio_chunks_transcriptions_txt"))
    os.environ.setdefault("DIR_FINAL_TRANSCRIPTION", str(repo / "05_audio_final_transcription"))

    # Necessário na etapa 01
    os.environ.setdefault("CHUNK_DURATION_SECONDS", "900")


def _list_input_files(input_dir: Path) -> list[Path]:
    exts = {".aac", ".m4a", ".mp3", ".wav", ".flac", ".ogg", ".opus", ".wma", ".mp4"}
    if not input_dir.exists():
        return []
    return sorted(
        [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    )


def main() -> int:
    repo = _repo_root()
    _set_default_envs(repo)

    steps = [
        (1, "01_split_audio_chunks"),
        (2, "02_adjust_volume_chunks"),
        (3, "03_convert_to_mp3"),
        (4, "04_transcribe_chunks"),
        (5, "05_merge_transcriptions"),
    ]

    input_dir = repo / "00_input_raw_audio"
    input_files = _list_input_files(input_dir)
    if not input_files:
        raise SystemExit(f"Nenhum arquivo de áudio encontrado em: {input_dir}")

    # Garante que o pipeline comece limpo (sem apagar a pasta final).
    clean_pipeline.clean(keep_final=True)

    print(f"\n🚀 Iniciando pipeline para {len(input_files)} arquivo(s)...")
    overall_start = time.time()
    last_result: object = None

    for idx, audio_path in enumerate(input_files, start=1):
        print(f"\n==============================")
        print(f"Arquivo {idx}/{len(input_files)}: {audio_path.name}")
        print(f"==============================")

        # Usado na etapa 05 (nome do arquivo final).
        os.environ["INPUT_AUDIO_AAC"] = str(audio_path)

        for step_num, module_name in steps:
            print(f"\n=== Etapa {step_num:02d}: {module_name}.py ===")
            start = time.time()
            if step_num == 1:
                last_result = _run_step_01_split(str(audio_path))
            else:
                last_result = _run_step(module_name)
            elapsed = time.time() - start
            print(f"⏱️  Etapa {step_num:02d} concluída em {elapsed:.2f}s")

        # Limpa intermediários ao final de cada arquivo, mantendo a saída final.
        clean_pipeline.clean(keep_final=True)

    total_elapsed = time.time() - overall_start
    print(f"\n✅ Pipeline finalizado em {total_elapsed:.2f}s")
    if last_result is not None:
        print(f"📦 Resultado da última etapa: {last_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
