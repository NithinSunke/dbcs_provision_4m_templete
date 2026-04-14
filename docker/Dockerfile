FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_VENV=/opt/app-venv \
    OCI_CLI_VENV=/opt/oci-cli-venv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip jq ca-certificates iputils-ping netcat-openbsd procps postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv $APP_VENV \
    && $APP_VENV/bin/pip install --upgrade pip \
    && $APP_VENV/bin/pip install -r requirements.txt
RUN python -m venv $OCI_CLI_VENV \
    && $OCI_CLI_VENV/bin/pip install --upgrade pip \
    && $OCI_CLI_VENV/bin/pip install oci-cli \
    && ln -sf $OCI_CLI_VENV/bin/oci /usr/local/bin/oci

COPY . .

EXPOSE 8080
ENTRYPOINT ["python", "docker/entrypoint.py"]
CMD ["/opt/app-venv/bin/python", "run_server.py"]
