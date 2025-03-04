ARG BASE_IMAGE

FROM debian:12-slim as base-model-downloader
RUN apt update && apt install aria2 -y
FROM ${BASE_IMAGE} as final

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=all

# 2️⃣ Değişkenleri compose'den al
ARG PYTORCH_VERSION
ARG WORKDIR

# 3️⃣ Çalışma dizinini belirle
WORKDIR ${WORKDIR}

# 4️⃣ Gerekli bağımlılıkları yükle
RUN apt update && apt install -y \
    python3 python3-pip git curl wget unzip \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Python bağımlılıklarını yükle

COPY test_input.json ${WORKDIR}/test_input.json
COPY requirements.txt ${WORKDIR}/requirements.txt
RUN python3 -m pip install --no-cache-dir -r ${WORKDIR}/requirements.txt

# 6️⃣ Hugging Face API Key'i çevresel değişken olarak ayarla
ARG HUGGINGFACE_ACCESS_TOKEN
ENV HUGGINGFACE_ACCESS_TOKEN=${HUGGINGFACE_ACCESS_TOKEN}


COPY script/* ${WORKDIR}/.

COPY script/llm_service.py ${WORKDIR}/llm_service.py
COPY script/rp_handler.py ${WORKDIR}/rp_handler.py

ARG PYTORCH_VERSION
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==${PYTORCH_VERSION} jupyterlab && \
    pip install -r requirements.txt

COPY script/* .

RUN chmod +x ./setup-ssh.sh

RUN ./setup-ssh.sh

EXPOSE 8188 8888

CMD ["/workspace/start.sh"]