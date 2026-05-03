# Desafio Técnico: Plataforma de Recomendação de Parâmetros

Pipeline experimental que recebe comandos de voz (áudio), transcreve usando STT local (Whisper), e extrai saídas estruturadas JSON utilizando LLM (Groq API - Llama 3).

## Como Executar

1. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -e ".[dev]"
   ```
3. Configure as variáveis de ambiente:
   - Certifique-se de que o arquivo `.env` na raiz do projeto contenha sua `GROQ_API_KEY`.
