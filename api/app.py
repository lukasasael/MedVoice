"""
MedVoice API — FastAPI backend que expõe o pipeline STT + LLM via HTTP.
"""

import os
import sys
import uuid
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Garante que src/ seja encontrado ao rodar de qualquer diretório
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.stt_module import STTModule
from src.llm_extractor import LLMExtractor

# ---------------------------------------------------------------------------
# Estado global (modelos carregados uma única vez)
# ---------------------------------------------------------------------------
pipeline: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega Whisper e LLM na inicialização do servidor."""
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    print(f"[startup] Carregando Whisper '{whisper_model}'...")
    pipeline["stt"] = STTModule(model_name=whisper_model)
    print("[startup] Inicializando LLM Extractor...")
    pipeline["llm"] = LLMExtractor()
    print("[startup] Pipeline pronto.")
    yield
    pipeline.clear()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MedVoice API",
    description="Pipeline STT + LLM para extração de comandos de equipamentos médicos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas de resposta
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    whisper_model: str


class ProcessingResponse(BaseModel):
    status: str
    transcription: str
    extracted_data: dict


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse, tags=["infra"])
def health_check():
    """Verifica se a API e o pipeline estão operacionais."""
    return {"status": "ok", "whisper_model": os.getenv("WHISPER_MODEL", "base")}


@app.post("/api/processar-audio", response_model=ProcessingResponse, tags=["pipeline"])
async def processar_audio(file: UploadFile = File(...)):
    """
    Recebe um arquivo de áudio (webm, mp3, wav, m4a),
    transcreve via Whisper e extrai entidades via LLM (Variante B híbrida).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo de áudio não fornecido.")

    extension = os.path.splitext(file.filename)[-1].lower() or ".webm"
    allowed = {".webm", ".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    if extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{extension}' não suportado. Use: {', '.join(allowed)}",
        )

    tmp_path = os.path.join(
        tempfile.gettempdir(), f"medvoice_{uuid.uuid4().hex}{extension}"
    )
    try:
        content = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)

        # 1. Transcrição (Whisper)
        try:
            transcription = pipeline["stt"].transcribe(tmp_path)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erro no STT: {exc}") from exc

        if not transcription.strip():
            raise HTTPException(
                status_code=422,
                detail="Áudio sem fala detectada. Verifique o microfone.",
            )

        # 2. Extração de entidades — Variante B (híbrida)
        try:
            extraction = pipeline["llm"].extract_hybrid(transcription)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erro no LLM: {exc}") from exc

        return {
            "status": "success",
            "transcription": transcription,
            "extracted_data": extraction.model_dump(),
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
