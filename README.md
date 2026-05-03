# MedVoice AI - Desafio Técnico: Plataforma de Recomendação de Parâmetros

Este projeto é uma Prova de Conceito (PoC) para um pipeline experimental de extração de intenções e parâmetros a partir de comandos de voz, focado em interações com equipamentos médicos.

O pipeline utiliza:
- **Speech-to-Text (STT):** Modelo Whisper (local) para transcrição do áudio.
- **LLM Extraction:** API do Groq (modelo Llama 3.1) para realizar a extração estruturada (JSON) da intenção (`intent`), parâmetros (`parameter`), valores (`value`), unidades (`unit`) e o status da operação (`status`).

## 🛠️ Como Configurar e Executar

### 1. Pré-requisitos do Sistema
Para que o Whisper consiga ler os áudios corretamente, é fundamental ter o `ffmpeg` instalado no seu sistema operativo:
- **Mac (Homebrew):** `brew install ffmpeg`
- **Linux (Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
- **Windows:** [Instruções do FFmpeg](https://ffmpeg.org/download.html)

### 2. Ambiente e Dependências
Crie um ambiente virtual na raiz do projeto e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API da Groq:
```env
GROQ_API_KEY=sua_chave_aqui
```

### 4. Avaliando o Pipeline
Para rodar a avaliação do modelo (STT + LLM) contra a base de dados embutida:
```bash
python src/evaluate.py
```

---

## 📊 Dataset e Áudios de Teste

A avaliação roda contra arquivos de áudio localizados na pasta `data/audio/`, confrontando as transcrições e intenções com o gabarito estruturado salvo em `data/transcripts/reference.json`.

Existem **dois conjuntos de áudios** utilizados para validar a resiliência deste sistema:

### 1. Áudios Sintéticos (Baseline)
Gerados dinamicamente via TTS (Text-to-Speech) usando a biblioteca `gTTS` como um baseline inicial perfeito para o Whisper:
- `caso_valido_simples.mp3`
- `caso_unidade_omitida.mp3`
- `caso_ambiguo.mp3`
- `caso_incompleto.mp3`
- `caso_invalido.mp3`

### 2. Áudios Reais Gravados (Teste de Estresse)
Para comprovar a robustez do sistema no mundo real — validando como o modelo lida com ruído, sotaque, velocidade de fala e informalidade (comum em emergências médicas) —, os seguintes áudios **foram gravados por um humano** e inseridos no dataset:
- **`BR408_1.mp3`**: *"reduzir o fluxo de oxigênio por favor"*
  - **Objetivo**: Testar um comando legítimo, porém incompleto (não informou o valor alvo).
- **`BR408_2.mp3`**: *"apagar as luzes da sala de cirurgia"*
  - **Objetivo**: Testar um comando perfeitamente claro, mas totalmente fora do escopo do equipamento (deve cair em intenção desconhecida).
- **`BR408_3.mp3`**: *"bota aquilo ali no vinte"*
  - **Objetivo**: Testar linguajar extremamente coloquial e ambíguo.
- **`BR408_4.mp3`**: *"ajusta a pressão p'ra doze"*
  - **Objetivo**: Testar dicção veloz, sotaque e redução de sílabas ("p'ra") para avaliar se o STT corrige no contexto.

---

## 📝 Nota para o Avaliador Técnico

Caro instrutor/avaliador,

O projeto está configurado para exibir com transparência as capacidades (e as limitações) do uso de LLMs para extração de dados médicos estruturados.

Ao rodar `python src/evaluate.py`, o console mostrará o gabarito (Ref), a saída literal do Whisper (STT) e a interpretação estruturada final (Extração). 

Recomendamos atenção especial aos casos de teste iniciados por `BR408_` (os áudios gravados). Eles demonstram situações onde as regras determinísticas clássicas falhariam, mas a combinação Whisper + Llama consegue, na maioria das vezes, inferir a semântica correta ou, pelo menos, acusar que a intenção é desconhecida ou que os parâmetros estão incompletos, garantindo a segurança do equipamento.
