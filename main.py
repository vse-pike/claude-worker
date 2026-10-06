"""claude-worker — HTTP-мост к claude -p: один запрос — один запуск агента."""
import asyncio
import os

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

CLAUDE_DIR = os.getenv("CLAUDE_DIR", ".")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT_SEC", "900"))

app = FastAPI()


class Run(BaseModel):
    prompt: str
    allowed_tools: list[str] = []
    timeout_sec: int = DEFAULT_TIMEOUT


@app.post("/run")
async def run(r: Run) -> Response:
    args = ["claude", "-p", "--output-format", "json"]
    if r.allowed_tools:
        args += ["--allowed-tools", ",".join(r.allowed_tools)]

    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=CLAUDE_DIR,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(r.prompt.encode()), timeout=r.timeout_sec)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise HTTPException(status_code=504, detail="claude timeout")

    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=err.decode()[-2000:])
    return Response(content=out, media_type="application/json")
