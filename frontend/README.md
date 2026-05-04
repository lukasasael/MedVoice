# MedVoice Frontend — Como Usar

## Pré-requisito
A API deve estar rodando em `http://localhost:8000` antes de abrir o frontend.

## Opção 1 — Abrir direto no browser (mais simples)
```bash
open frontend/index.html
```

## Opção 2 — Servir via HTTP local (recomendado para evitar restrições de CORS)
```bash
# Python (disponível em qualquer sistema com Python 3)
python -m http.server 5500 --directory frontend/

# Acesse em: http://localhost:5500
```

## O que a interface faz

1. **Verifica** automaticamente se a API está online (indicador no header)
2. **Grava** o áudio via microfone do browser ao clicar no botão
3. **Envia** para a API e exibe o resultado estruturado:
   - Transcrição literal do Whisper
   - Intenção, parâmetro, valor e unidade extraídos pelo LLM
   - Badge de status (OK / AMBÍGUO / INCOMPLETO / INVÁLIDO)
   - Alerta visual se o comando requer confirmação
4. **Histórico** das últimas 5 gravações da sessão

## Formatos de áudio suportados
O browser grava automaticamente no formato suportado pelo sistema (`.webm`, `.mp4` ou `.ogg`).
O ffmpeg instalado no sistema permite que o Whisper leia todos esses formatos.
