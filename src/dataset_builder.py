import os
import json
from gtts import gTTS

AUDIO_DIR = "data/audio"
TRANSCRIPT_DIR = "data/transcripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

test_cases = [
    {
        "id": "caso_valido_simples",
        "text": "ajustar a frequência para cinco hertz",
        "expected_intent": "ajustar_parametro"
    },
    {
        "id": "caso_unidade_omitida",
        "text": "coloca a temperatura em trinta e seis",
        "expected_intent": "ajustar_parametro"
    },
    {
        "id": "caso_ambiguo",
        "text": "aumenta aquilo lá para dez",
        "expected_intent": "ajustar_parametro"
    },
    {
        "id": "caso_incompleto",
        "text": "ajustar a pressão para",
        "expected_intent": "ajustar_parametro"
    },
    {
        "id": "caso_invalido",
        "text": "preparar café expresso",
        "expected_intent": "desconhecido"
    }
]

def generate_audio():
    print("Gerando áudios sintéticos...")
    for case in test_cases:
        filepath = os.path.join(AUDIO_DIR, f"{case['id']}.mp3")
        if not os.path.exists(filepath):
            tts = gTTS(text=case['text'], lang='pt')
            tts.save(filepath)
            print(f"Gerado: {filepath}")
        else:
            print(f"Já existe: {filepath}")
    
    # Save the reference map
    ref_path = os.path.join(TRANSCRIPT_DIR, "reference.json")
    with open(ref_path, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)
    print("Dataset de referência salvo.")

if __name__ == "__main__":
    generate_audio()
