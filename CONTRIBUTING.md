# Contribuir a MANGA Studio — Guía rápida

Gracias por colaborar. Este documento explica cómo preparar el entorno y ejecutar la CLI con detección automática de hardware y validación de modelos.

1. Requisitos mínimos
   - Python 3.10+
   - Git
   - SSD recomendado y al menos 50 GB libres (para modelos y caché)
2. Entorno
   - Crea y activa un virtualenv:
     - python -m venv .venv
     - source .venv/bin/activate   # Linux / Mac
     - .\.venv\Scripts\activate    # Windows
   - Instalar dependencias mínimas:
     - pip install -r requirements.txt
   - Nota: torch y librerías ML se instalan aparte según la GPU/cuda disponible.
3. Ejecutar detectores
   - Desde la raíz del repo:
     - PYTHONPATH=src python -m manga_studio --synopsis "Elena está en un castillo gótico..."
   - Para ver solo la detección:
     - PYTHONPATH=src python -c "from manga_studio.hardware import detect_system; import json; print(json.dumps(detect_system(), indent=2))"

4. Dónde colocar los modelos

   La suite busca los modelos en la carpeta raíz de modelos indicada en `src/config/models.json` (por defecto `models/` relativa al repo).

   Puedes definir una ruta alternativa mediante la variable de entorno `MANGA_MODELS_PATH` que tendrá prioridad sobre la config.

   Estructura recomendada dentro de la carpeta raíz de modelos:

     models/image/sd-1.5/
     models/asr/whisper-small/
     models/tts/coqui-small/
     models/llm/ggml-7b.bin

   - No incluyas modelos en el repositorio. Coloca los ficheros en la ruta anterior y la suite los detectará automáticamente.
   - Si prefieres otra ubicación, define la variable de entorno `MANGA_MODELS_PATH` apuntando a la carpeta raíz de modelos.

5. Ramas y PRs
   - Usa ramas `feat/`, `fix/`, `docs/`.
   - PRs hacia `main`, con descripción clara y referencia a issues relacionados.

6. Política de modelos
   - No incluimos modelos en el repositorio.
   - Documenta enlaces y licencias en /docs cuando integres un modelo.

7. Contacto
   - Usa issues para proponer cambios de arquitectura o nuevos módulos.

End of changes.
