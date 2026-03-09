"""
Limpa todos os diretórios gerados pelo pipeline.

Por padrão: limpa chunks + mp3 + transcrições + pasta final.
Não remove o áudio de entrada em `00_input_raw_audio/`.

Uso:
  python clean_pipeline.py
  python clean_pipeline.py --keep-final
"""

from __future__ import annotations

import argparse
import shutil
import os
from pathlib import Path

from dotenv import load_dotenv


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _clear_dir_keep_folder(target_dir: Path) -> int:
    """Remove tudo dentro de target_dir, mantendo a pasta."""
    if not target_dir.exists():
        return 0

    removed = 0
    for child in sorted(target_dir.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)
        removed += 1
    return removed


def clean(*, keep_final: bool = False) -> int:
    """
    Limpa os diretórios intermediários do pipeline.

    - keep_final=False (padrão): também limpa `05_final_transcription/`
    - keep_final=True: mantém `05_final_transcription/`
    """
    load_dotenv()
    repo = _repo_root()

    def _dir_from_env(env_key: str, fallback_dirname: str) -> Path:
        raw = Path(os.getenv(env_key, fallback_dirname))
        return (repo / raw).resolve() if not raw.is_absolute() else raw.resolve()

    # Diretórios do pipeline (dentro do repositório).
    # Importante: NÃO limpar `00_input_raw_audio/` (é a fila de entrada).
    dirs: list[Path] = [
        _dir_from_env("DIR_CHUNKS_ORIGINAL_AAC", "01_audio_chunks_original_aac"),
        _dir_from_env("DIR_CHUNKS_VOLUME_ADJUSTED_AAC", "02_audio_chunks_volume_adjusted_aac"),
        _dir_from_env("DIR_CHUNKS_MP3", "03_audio_chunks_to_mp3"),
        _dir_from_env("DIR_TRANSCRIPTIONS", "04_audio_chunks_transcriptions_txt"),
    ]
    final_dir = _dir_from_env("DIR_FINAL_TRANSCRIPTION", "05_audio_final_transcription")
    if not keep_final:
        dirs.append(final_dir)

    print("🧹 Limpando diretórios do pipeline...")
    total_removed = 0
    for path in dirs:
        print(f"\n📂 {path}")
        removed = _clear_dir_keep_folder(path)
        print(f"✅ Itens removidos: {removed}")
        total_removed += removed

    print(f"\n✅ Limpeza concluída. Total de itens removidos: {total_removed}")
    return total_removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Limpa diretórios de saída do pipeline.")
    parser.add_argument(
        "--keep-final",
        action="store_true",
        help="Mantém a pasta de transcrição final (não limpa).",
    )
    args = parser.parse_args()

    clean(keep_final=args.keep_final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
