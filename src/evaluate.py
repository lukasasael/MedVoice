import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import jiwer
from src.stt_module import STTModule
from src.llm_extractor import LLMExtractor

AUDIO_DIR = "data/audio"
TRANSCRIPT_DIR = "data/transcripts"

def evaluate_pipeline():
    ref_path = os.path.join(TRANSCRIPT_DIR, "reference.json")
    if not os.path.exists(ref_path):
        print("Dataset de referência não encontrado. Rode python src/dataset_builder.py primeiro.")
        return

    with open(ref_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    stt = STTModule()
    extractor = LLMExtractor()

    references = []
    hypotheses = []
    
    print("\nIniciando Avaliação do STT e LLM...\n")
    
    for item in dataset:
        audio_path = os.path.join(AUDIO_DIR, f"{item['id']}.mp3")
        if not os.path.exists(audio_path):
            continue
            
        print(f"[{item['id']}] Processando...")
        # 1. Transcrição (STT)
        transcription = stt.transcribe(audio_path)
        
        references.append(item['text'].lower())
        hypotheses.append(transcription.lower())
        
        # 2. Extração Estruturada (Variante B Híbrida)
        extraction = extractor.extract_hybrid(transcription)
        
        # Avaliação de Intent
        intent_match = extraction.intent == item['expected_intent']
        print(f"  Ref: '{item['text']}'")
        print(f"  STT: '{transcription}'")
        print(f"  Intent Esperado: {item['expected_intent']} | Extraído: {extraction.intent} -> {'✅' if intent_match else '❌'}")
        print(f"  Status da Extração: {extraction.status}")
        print("-" * 40)

    # Métricas STT
    wer = jiwer.wer(references, hypotheses)
    cer = jiwer.cer(references, hypotheses)
    
    print("\n--- RESULTADOS FINAIS (Sintéticos) ---")
    print(f"Word Error Rate (WER): {wer:.2%}")
    print(f"Character Error Rate (CER): {cer:.2%}")
    
    print("\n> [!NOTE]")
    print("> Como estes áudios são gerados via TTS (Sintéticos), o WER/CER tende a ser próximo de 0%.")
    print("> Para a avaliação final do Líder Técnico, grave áudios reais com ruído, adicione na pasta")
    print("> data/audio/ e atualize o reference.json para medir a verdadeira robustez do LLM contra falhas do STT.")

if __name__ == "__main__":
    evaluate_pipeline()
