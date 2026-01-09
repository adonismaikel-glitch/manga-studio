"""
Model Manager para MANGA Studio

- Lee src/config/models.json
- Prioriza la variable de entorno MANGA_MODELS_PATH si está definida
- Valida presencia/formato mínimo de los modelos esperados
- Expone validate_models() que devuelve un dict con estado por modelo
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PACKAGE_ROOT / "config" / "models.json"
ENV_MODELS_PATH = "MANGA_MODELS_PATH"


def load_models_config(config_path: Path | str | None = None) -> Dict[str, Any]:
    p = Path(config_path) if config_path else DEFAULT_CONFIG
    if not p.exists():
        raise FileNotFoundError(f"models.json no encontrado en: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _resolve_path(raw_path: str, env_root: str | None) -> Path:
    rp = Path(raw_path)
    if rp.is_absolute():
        return rp
    if env_root:
        return Path(env_root) / rp
    return Path(raw_path)


def _check_diffusers_dir(p: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if not p.exists():
        reasons.append("ruta no existe")
        return False, reasons
    if p.is_file():
        if p.suffix in {".safetensors", ".ckpt", ".bin"}:
            return True, reasons
        reasons.append(f"archivo inesperado: {p.name}")
        return False, reasons
    candidates = {"model_index.json", "unet", "pytorch_model.bin", "vae", "safety_checker"}
    if any((p / c).exists() for c in candidates):
        return True, reasons
    if any(p.glob("*.safetensors")):
        return True, reasons
    reasons.append("no se encontraron archivos esperados de diffusers (.safetensors, model_index.json, pytorch_model.bin, carpeta unet)")
    return False, reasons


def _check_whisper_dir(p: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if not p.exists():
        reasons.append("ruta no existe")
        return False, reasons
    if p.is_file():
        if p.suffix in {".bin", ".pt", ".pth"}:
            return True, reasons
        reasons.append(f"archivo inesperado: {p.name}")
        return False, reasons
    if any((p / f).exists() for f in ("pytorch_model.bin", "config.json", "tokenizer.json")):
        return True, reasons
    reasons.append("no se encontraron archivos esperados de Whisper (pytorch_model.bin, config.json)")
    return False, reasons


def _check_coqui_dir(p: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if not p.exists():
        reasons.append("ruta no existe")
        return False, reasons
    if p.is_file():
        reasons.append("esperado directorio para Coqui, se encontró archivo")
        return False, reasons
    if any((p / f).exists() for f in ("config.json", "model.py", "tts_config.json")):
        return True, reasons
    if any(p.glob("*.pth")) or any(p.glob("*.pt")):
        return True, reasons
    reasons.append("no se encontraron archivos típicos de Coqui (config.json, *.pth)")
    return False, reasons


def _check_ggml_file(p: Path) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if p.exists() and p.is_file():
        if p.suffix in {".bin", ".gguf", ".ggml"} or p.name.endswith(".bin"):
            return True, reasons
        reasons.append("archivo presente pero extensión inesperada para ggml")
        return False, reasons
    reasons.append("archivo ggml no encontrado")
    return False, reasons


TYPE_CHECKERS = {
    "diffusers": _check_diffusers_dir,
    "whisper": _check_whisper_dir,
    "coqui": _check_coqui_dir,
    "ggml": _check_ggml_file,
}


def validate_models(config_path: Path | str | None = None) -> Dict[str, Any]:
    cfg = load_models_config(config_path)
    env_root = os.environ.get(ENV_MODELS_PATH)
    results: Dict[str, Any] = {}
    cfg_root = cfg.get("root_models_path") if isinstance(cfg, dict) else None
    root_used = env_root or cfg_root

    for key, entry in cfg.items():
        if key == "root_models_path":
            continue
        raw_path = entry.get("path", "")
        if not raw_path:
            results[key] = {"present": False, "errors": ["entry sin campo 'path'"], "resolved_path": None}
            continue
        rp = Path(raw_path)
        if not rp.is_absolute():
            if env_root:
                resolved = Path(env_root) / rp
            elif cfg_root:
                resolved = Path(cfg_root) / rp
            else:
                resolved = (PACKAGE_ROOT.parent / rp).resolve()
        else:
            resolved = rp
        resolved = resolved.expanduser().resolve()
        mtype = entry.get("type", "").lower()
        checker = TYPE_CHECKERS.get(mtype)
        present = False
        errors: List[str] = []
        if checker:
            present, errors = checker(resolved)
        else:
            if resolved.exists():
                present = True
            else:
                present = False
                errors.append("ruta no encontrada (checker genérico)")

        results[key] = {
            "present": present,
            "errors": errors,
            "resolved_path": str(resolved),
            "type": mtype,
            "name": entry.get("name"),
        }

    return {
        "root_used": root_used,
        "config_path": str(DEFAULT_CONFIG),
        "results": results,
    }


def main():
    import json
    out = validate_models()
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
