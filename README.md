# DocDigester2MD

Convierte automáticamente documentos, imágenes, audio y vídeos de YouTube a Markdown. El proceso se dispara mediante GitHub Actions cada vez que se sube un archivo a la carpeta `input/`.

---

## Cómo añadir archivos

### Desde la web de GitHub
1. Navega a la carpeta `input/` del repositorio.
2. Haz clic en **Add file → Upload files**.
3. Arrastra o selecciona el archivo y haz commit directamente a `main`.
4. El Action arrancará automáticamente en segundos.

### Desde la línea de comandos
```bash
cp mi_documento.pdf input/
git add input/mi_documento.pdf
git commit -m "feat: add mi_documento"
git push
```

### Ejecución manual
Ve a **Actions → DocDigester2MD → Run workflow** para disparar el proceso sin subir archivos nuevos.

---

## Configuración de Secrets en GitHub

Ve a **Settings → Secrets and variables → Actions → New repository secret** y crea los tres secrets siguientes:

| Secret | Descripción | Ejemplo |
|---|---|---|
| `AI_API_KEY` | API key compatible con la API de OpenAI | `sk-ant-...` |
| `AI_BASE_URL` | URL base del endpoint | `https://api.anthropic.com/v1` |
| `AI_MODEL` | Modelo a utilizar | `claude-sonnet-4-6` |

---

## Formatos soportados

| Extensión | Tipo | Método de conversión |
|---|---|---|
| `.pdf` | Documento | markitdown |
| `.docx` | Documento | markitdown |
| `.pptx` | Presentación | markitdown |
| `.xls` / `.xlsx` | Hoja de cálculo | markitdown |
| `.png` / `.jpg` / `.jpeg` / `.webp` / `.gif` | Imagen | markitdown + visión LLM |
| `.mp3` / `.wav` / `.m4a` / `.ogg` | Audio | Whisper local (modelo `base`) |
| `.url` / `.txt` | YouTube | youtube_transcript_api → yt-dlp + Whisper |

Para archivos `.url` o `.txt`, el contenido del archivo debe incluir una URL de YouTube con el formato estándar (`https://www.youtube.com/watch?v=...` o `https://youtu.be/...`).

---

## Ejemplo de frontmatter YAML generado

Cada Markdown generado comienza con un bloque de metadatos:

```yaml
---
original_file: informe_anual.pdf
processed_date: 2026-04-22T10:30:00Z
file_type: pdf
size_bytes: 2457600
---
```

---

## Estructura del output generado

```
output/
├── informe_anual.md        # ← mismo nombre base que el original
├── presentacion_q1.md
├── entrevista_podcast.md
├── tutorial_youtube.md
└── errors.log              # solo si hubo errores parciales
```

El archivo `processed.yaml` en la raíz registra cada archivo procesado:

```yaml
informe_anual.pdf:
  hash: a3f8c1...
  processed_at: 2026-04-22T10:30:00Z
  output: informe_anual.md
```

Si se vuelve a subir el mismo archivo sin cambios, se omite el reprocesado. Si el archivo cambió (hash distinto), se reprocesa y el `.md` se sobreescribe.

---

## Limitaciones conocidas

| Limitación | Detalle |
|---|---|
| Tamaño máximo de archivo | 100 MB (límite de GitHub) |
| Tiempo máximo de ejecución | 6 horas (límite de GitHub Actions) |
| Precisión de transcripción | Whisper modelo `base` — velocidad alta, precisión media |
| YouTube sin transcripción | Algunos vídeos no tienen subtítulos; el fallback a Whisper requiere descargar el audio completo |
| Ejecución en CPU | Whisper corre en CPU en el entorno de Actions — archivos de audio largos tardarán más |

---

## Cómo cambiar de proveedor de IA

Solo hay que actualizar los tres secrets del repositorio:

| Proveedor | `AI_API_KEY` | `AI_BASE_URL` | `AI_MODEL` |
|---|---|---|---|
| Anthropic (Claude) | `sk-ant-...` | `https://api.anthropic.com/v1` | `claude-sonnet-4-6` |
| OpenAI | `sk-...` | `https://api.openai.com/v1` | `gpt-4o` |
| OpenRouter | `sk-or-...` | `https://openrouter.ai/api/v1` | `anthropic/claude-3.5-sonnet` |

No es necesario modificar el código ni el workflow.

---

## Uso como GitHub Action (reutilizable)

El proyecto se publica como Action Docker. Cualquier repositorio puede invocarlo:

```yaml
- uses: actions/checkout@v4
- uses: erseco/DocDigester2MD@v1
  with:
    ai_api_key: ${{ secrets.AI_API_KEY }}
    ai_base_url: ${{ secrets.AI_BASE_URL }}
    ai_model: ${{ secrets.AI_MODEL }}
```

La Action usa la imagen pre-construida `ghcr.io/erseco/docdigester2md:latest` (ligera, sin
Whisper). Procesa los archivos de `input/` y escribe los `.md` en `output/`. Para transcripción
de audio/YouTube usa la imagen con Whisper (`:audio`) mediante un paso `container:` o
`docker run` propio.

---

## Uso con Docker

Imagen ligera (documentos e imágenes — recomendada por defecto):

```bash
docker pull ghcr.io/erseco/docdigester2md:latest

docker run --rm \
  -e AI_API_KEY=sk-ant-... \
  -e AI_BASE_URL=https://api.anthropic.com/v1 \
  -e AI_MODEL=claude-sonnet-4-6 \
  -v "$PWD/input:/app/input" \
  -v "$PWD/output:/app/output" \
  -v "$PWD/processed:/app/processed" \
  ghcr.io/erseco/docdigester2md:latest
```

Imagen con audio (incluye Whisper + torch + ffmpeg, mucho más pesada):

```bash
docker run --rm ... ghcr.io/erseco/docdigester2md:audio
```

Construir localmente:

```bash
docker build -t docdigester2md:latest .                          # ligera
docker build --build-arg INCLUDE_AUDIO=true -t docdigester2md:audio .  # con audio
```

> **Nota:** las dependencias pesadas (`torch`, `torchaudio`, `openai-whisper`, `yt-dlp`) viven en
> `requirements-audio.txt` y solo se instalan en la variante `:audio`. La imagen por defecto es
> ligera y arranca rápido. El estado de procesado se guarda en `processed.yaml`.
