# MedVoice API — Como Rodar

## Pré-requisitos
- `ffmpeg` instalado no sistema
- Arquivo `.env` na raiz do projeto com `GROQ_API_KEY=sua_chave`

## Instalar dependências da API
```bash
# Da raiz do projeto Desafio_IA:
source .venv/bin/activate
pip install fastapi uvicorn python-multipart
```

## Rodar o servidor
```bash
# Da raiz do projeto:
uvicorn api.app:app --reload --port 8000
```

## Endpoints
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/health` | Status do servidor e modelo carregado |
| POST | `/api/processar-audio` | Recebe áudio e retorna JSON extraído |

## Variáveis de Ambiente
| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `GROQ_API_KEY` | — | Chave da API Groq (obrigatória) |
| `WHISPER_MODEL` | `base` | Modelo Whisper (`tiny`, `base`, `small`, `medium`) |

## Documentação interativa
Acesse `http://localhost:8000/docs` para o Swagger UI gerado automaticamente.
