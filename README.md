# claude-worker

HTTP-сервис «прогони промпт через `claude -p`». Один контейнер с claude-code и MCP;
разные системы (agentd, cron-джобы) ходят в него по сети, каждому — свой набор тулов.

## API

`POST /run`

```json
{
  "prompt": "Задача #7 ...",
  "allowed_tools": ["mcp__general-mcp__send_message"],
  "timeout_sec": 900
}
```

`allowed_tools` и `timeout_sec` необязательны (дефолт таймаута — 900 с, env `DEFAULT_TIMEOUT_SEC`).
Ответ — stdout `claude --output-format json` как есть: `{"is_error": bool, "result": "..."}`.
Ненулевой exit claude → 500 с stderr, таймаут → 504.

## Запуск

```sh
docker network create agentnet   # один раз, общая с whisper/agentd (external для всех)
docker compose up -d
docker compose exec claude-worker claude   # один раз залогиниться (/login), сотрётся только при docker volume rm
```

`.mcp.json` кладётся в `./workspace/` (монтируется в `/workspace`, там claude и работает).
Хостовый MCP доступен контейнеру как `http://host.docker.internal:8080` (compose добавляет
`host.docker.internal:host-gateway` — работает и на Linux). Альтернатива логину —
`CLAUDE_CODE_OAUTH_TOKEN` в `.env`.

## Как подключить consumer

Присоединить свой compose-проект к сети `agentnet` и дёрнуть `http://claude-worker:8090/run`:

```yaml
services:
  my-bot:
    environment:
      WORKER_URL: http://claude-worker:8090
networks:
  default:
    name: agentnet
    external: true
```
