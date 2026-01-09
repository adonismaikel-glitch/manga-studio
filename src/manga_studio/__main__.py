#!/usr/bin/env python3
"""
CLI mínima que integra la detección de hardware y la estimación MVP.
Al arrancar, detecta el hardware y muestra la recomendación de perfil y valida modelos.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

from manga_studio.hardware import detect_system, load_profiles, classify_tier
from manga_studio.model_manager import validate_models

console = Console()
HERE = Path(__file__).resolve().parent.parent
DEFAULT_PROFILES = HERE / "config" / "hardware_profiles.json"

def estimate_shots_and_keyframes(text: str) -> dict:
    words = len(text.split())
    shots = max(1, (words + 99) // 100)
    keyframes = shots * 3
    duration_seconds = shots * 30
    return {
        "words": words,
        "shots": shots,
        "keyframes": keyframes,
        "duration_seconds": duration_seconds,
    }

def show_system_and_profile(info: dict, profile: dict):
    table = Table(title="MANGA Studio - Hardware detection")
    table.add_column("Propiedad")
    table.add_column("Valor")
    table.add_row("OS", info.get("os", "unknown"))
    table.add_row("RAM (GB)", str(info.get("ram_total_gb", "unknown")))
    table.add_row("Disk free (GB)", str(info.get("disk_free_gb", "unknown")))
    table.add_row("GPU count", str(info.get("gpu_count", 0)))
    if info.get("gpus"):
        for g in info["gpus"]:
            table.add_row("GPU", f"{g.get('name')} ({g.get('total_memory_gb')} GB)")
    table.add_row("Profile", profile.get("profile_name", "unknown"))
    table.add_row("Model recommendation", profile.get("model_recommendation", ""))
    console.print(table)

def show_model_status(report: dict):
    table = Table(title="Model Manager - estado de modelos")
    table.add_column("Modelo")
    table.add_column("Tipo")
    table.add_column("Estado")
    table.add_column("Ruta resuelta")
    table.add_column("Errores")
    for k, v in report.get("results", {}).items():
        state = "OK" if v.get("present") else "MISSING"
        errors = "; ".join(v.get("errors") or [])
        table.add_row(str(k), str(v.get("type") or ""), state, str(v.get("resolved_path") or ""), errors)
    console.print(table)

def main():
    parser = argparse.ArgumentParser(prog="manga-studio", description="MANGA Studio MVP CLI")
    parser.add_argument("--synopsis", "-s", type=str, help="Sinopsis corta como texto")
    parser.add_argument("--file", "-f", type=str, help="Fichero de texto con la sinopsis")
    parser.add_argument("--profiles", type=str, default=str(DEFAULT_PROFILES), help="Ruta a hardware_profiles.json")
    args = parser.parse_args()

    # Detect hardware y perfil
    system = detect_system()
    profiles = load_profiles(args.profiles)
    profile = classify_tier(system, profiles)
    show_system_and_profile(system, profile)

    # Validar modelos disponibles (Model Manager)
    mm_report = validate_models()
    show_model_status(mm_report)

    # Si hay texto, ejecutamos la estimación MVP
    text = ""
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.synopsis:
        text = args.synopsis

    if text:
        res = estimate_shots_and_keyframes(text)
        console.print("[bold green]Estimación MVP[/bold green]")
        console.print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
