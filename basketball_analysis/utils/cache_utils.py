import hashlib
import json
from pathlib import Path


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_analysis_cache_key(video_path, model_paths, settings):
    """Build a cache key from exact input/model bytes and processing settings."""
    payload = {
        "video": sha256_file(video_path),
        "models": {
            Path(path).name: sha256_file(path)
            for path in sorted(str(Path(path).resolve()) for path in model_paths)
        },
        "settings": settings,
        "pipeline_schema": 1,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
