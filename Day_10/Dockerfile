# SmartNest Rental Platform — production image
# Build:  docker build -t smartnest-rental .
# Run:    docker run --rm -p 8000:8000 smartnest-rental

FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# OpenCV / ONNX runtime system libs
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgomp1 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (CPU-only PyTorch first to keep the image smaller)
COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --upgrade pip \
    && pip install \
        torch==2.2.2 \
        torchvision==0.17.2 \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r /app/server/requirements.txt \
    && pip uninstall -y opencv-python || true \
    && pip install --force-reinstall --no-cache-dir numpy==1.26.4 opencv-python-headless==4.10.0.84 \
    && python -c "import cv2, numpy; print('opencv', cv2.__version__, 'numpy', numpy.__version__)"

# Application code and ML assets only
COPY client /app/client
COPY server/server.py server/util.py /app/server/
COPY model/artifacts /app/model/artifacts
COPY models /app/models

WORKDIR /app/server

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

# Single worker: ML models are loaded in-process; extra workers duplicate memory.
CMD ["gunicorn", \
    "-w", "1", \
    "-k", "gthread", \
    "--threads", "4", \
    "-b", "0.0.0.0:8000", \
    "--timeout", "120", \
    "server:app"]
