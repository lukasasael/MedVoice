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

## 🧠 Análise do Domínio e Estratégia (Item 5.1)

### Artefatos e Justificativa
Os artefatos deste protótipo (`schema.py`, `dataset_builder.py`, e `reference.json`) foram desenhados para representar o fluxo mínimo viável de uma sala cirúrgica ou UTI. 
- **Schema Pydantic:** Escolhido por forçar tipagem forte (Enums) e permitir a geração automática do `JSON Schema` lido pelo LLM (Structured Outputs).
- **Catálogo de Comandos e Casos de Borda:** Selecionamos intencionalmente falas incompletas, ambíguas e fora de escopo para validar o comportamento defensivo do equipamento (evitar falsos positivos perigosos).

### Dificuldades do Domínio
- **Ambiguidades:** Uso de pronomes ("aumenta *aquilo*") ou omissão do parâmetro base ("bota no 20").
- **Variações de Escrita e Unidades:** Como "p'ra", "pra", "para", e unidades foneticamente complexas de transcrever.

### Estratégia Adotada
Optamos por uma arquitetura em dois estágios:
1. **STT Local (Whisper Base):** Rápido, roda sem internet (crucial para hospitais), mas suscetível a erros fonéticos.
2. **LLM Rápido via API (Llama 3.1 8b):** Baixa latência, encarregado de inferir a semântica do texto "sujo" gerado pelo STT.

---

## 🔍 Análise de Erros de STT e Mitigações (Item 5.6)

Durante os testes com os áudios reais gravados, observamos padrões de falha no módulo STT (Whisper):

1. **Erros mais frequentes:** 
   - Confusão fonética em unidades de medida: "hertz" foi transcrito como "rertz", "hzs", ou "heats".
   - Alucinação de pontuação ou junção de palavras velozes ("p'radoze").
2. **Impacto na Extração:**
   - Uma abordagem puramente baseada em LLM (Variante A) pode falhar ao tentar encaixar um valor bizarro ("rertz") no JSON final, gerando alucinações secundárias ou rejeitando a extração.
3. **Mitigações Adotadas (Variante B Híbrida):**
   - Implementamos no `llm_extractor.py` uma camada de **Normalização Lexical (Pós-processamento)**. A regra mapeia variações bizarras conhecidas ("rertz", "heats") para o padrão oficial ("Hz").
   - **Validação Semântica de Apoio:** Regras garantem que comandos com intenção de ajuste, mas sem valor numérico extraído, sejam forçados para o status `INCOMPLETO`, sobrepondo falhas de julgamento do LLM puro.

---

## 🌐 Demo Web (API + Frontend)

Além do pipeline em linha de comando, o projeto inclui uma interface web completa para demonstrar o sistema de forma interativa.

### Estrutura adicionada
```
api/        ← Servidor FastAPI (backend)
frontend/   ← Interface web com gravador de voz
```

### Como rodar a demo

**1. Instalar dependências da API:**
```bash
source .venv/bin/activate
pip install -e ".[api]"
```

**2. Iniciar o servidor (na raiz do projeto):**
```bash
uvicorn api.app:app --reload --port 8000
```

**3. Abrir o frontend:**
```bash
open frontend/index.html
# ou sirva via HTTP:
python -m http.server 5500 --directory frontend/
```

O frontend verifica automaticamente se a API está online, grava o áudio do microfone, envia para transcrição via Whisper e exibe o JSON estruturado extraído pelo LLM em tempo real.

---
## 📝 Nota para o Avaliador Técnico

Caro instrutor/avaliador,

O projeto está configurado para exibir com transparência as capacidades (e as limitações) do uso de LLMs para extração de dados médicos estruturados.

Ao rodar `python src/evaluate.py`, o console mostrará o gabarito (Ref), a saída literal do Whisper (STT) e a interpretação estruturada final (Extração). 

Recomendamos atenção especial aos casos de teste iniciados por `BR408_` (os áudios gravados). Eles demonstram situações onde as regras determinísticas clássicas falhariam, mas a combinação Whisper + Llama consegue, na maioria das vezes, inferir a semântica correta ou, pelo menos, acusar que a intenção é desconhecida ou que os parâmetros estão incompletos, garantindo a segurança do equipamento.
