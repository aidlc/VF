FROM ubuntu:24.04

# ── Locale / Timezone ────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TERM=xterm-256color
ENV COLORTERM=truecolor

# ── System packages ──────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        # locale / timezone
        locales tzdata \
        # build tools (required for pyenv / Python compilation)
        build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev libncursesw5-dev xz-utils \
        tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
        # runtime utilities
        curl wget git vim nano less ca-certificates gnupg \
        sudo htop tree jq unzip zip \
        openssh-client iputils-ping net-tools iproute2 \
    && locale-gen en_US.UTF-8 ja_JP.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# ── pyenv ────────────────────────────────────────────────────
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

RUN curl -fsSL https://pyenv.run | bash \
    && pyenv install 3.13.2 \
    && pyenv global 3.13.2 \
    && pyenv rehash

# ── uv package manager ───────────────────────────────────────
ENV PATH="/root/.local/bin:$PATH"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# ── nvm + Node.js 24.13.0 ────────────────────────────────────
ENV NVM_DIR="/root/.nvm"
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" \
    && nvm install 24.13.0 \
    && nvm alias default 24.13.0 \
    && nvm use default \
    && nvm cache clear

# Put the default Node on PATH so subsequent RUN commands and
# the running container can find node/npm without sourcing nvm.
RUN ln -s "$NVM_DIR/versions/node/v24.13.0/bin/node"   /usr/local/bin/node   && \
    ln -s "$NVM_DIR/versions/node/v24.13.0/bin/npm"    /usr/local/bin/npm    && \
    ln -s "$NVM_DIR/versions/node/v24.13.0/bin/npx"    /usr/local/bin/npx

# ── Cursor CLI ───────────────────────────────────────────────
# ~/.local/bin is already on PATH via the ENV above
RUN curl -fsS https://cursor.com/install | bash \
    && agent --version

# ── Shell config ─────────────────────────────────────────────
COPY .bashrc /root/.bashrc

# ── Workspace (bind-mount target) ────────────────────────────
RUN mkdir -p /workspace/docnova && chmod 777 /workspace/docnova
WORKDIR /workspace/docnova

# ── Verify versions at build time ────────────────────────────
RUN echo "=== Build verification ===" \
    && python --version \
    && uv --version \
    && node --version \
    && npm --version \
    && agent --version

# Keep container alive; exec into it with:  docker exec -it <name> bash
CMD ["bash", "--login", "-c", "sleep infinity"]
