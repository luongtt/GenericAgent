FROM python:3.11-slim

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true && \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y \
    git \
    curl \
    procps \
    wget \
    vim \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/luongtt/GenericAgent.git .

RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi && \
    pip install --no-cache-dir streamlit pywebview pyTelegramBotAPI python-telegram-bot beautifulsoup4

CMD ["python", "frontends/tgapp.py"]