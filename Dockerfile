# DocDigester2MD — converts documents/images/audio/YouTube to Markdown.
#
# By default builds a LIGHT image (no Whisper/torch). Build the audio variant
# with:  docker build --build-arg INCLUDE_AUDIO=true -t docdigester2md:audio .
FROM python:3.14-slim

ARG INCLUDE_AUDIO=false

WORKDIR /app

# Core (light) dependencies — always installed.
COPY requirements.txt requirements-audio.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Optional heavy audio stack (Whisper + torch) and ffmpeg.
RUN if [ "$INCLUDE_AUDIO" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends ffmpeg && \
        rm -rf /var/lib/apt/lists/* && \
        pip install --no-cache-dir -r requirements-audio.txt ; \
    fi

COPY DocDigester2MD.py docdigester.yaml ./
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
