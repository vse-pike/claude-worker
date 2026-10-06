FROM node:22-bookworm-slim
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates git python3 python3-pip \
	&& rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN npm install -g @anthropic-ai/claude-code \
	&& pip install --break-system-packages --no-cache-dir -r requirements.txt
COPY main.py ./
ENV CLAUDE_DIR=/workspace
ENV CLAUDE_DIR=/workspace
VOLUME /workspace
EXPOSE 8090
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
