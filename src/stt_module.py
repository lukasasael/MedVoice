import os

import whisper


class STTModule:
    def __init__(self, model_name: str = "base"):
        print(f"Carregando modelo Whisper '{model_name}' (isso pode demorar na primeira vez)...")
        # Load the whisper model. 'base' is fast on CPU and sufficient for experiments.
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcreve o arquivo de áudio especificado.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")

        result = self.model.transcribe(audio_path, language="pt")
        return result["text"].strip()


if __name__ == "__main__":
    # Teste rápido
    stt = STTModule()
    test_file = "data/audio/caso_valido_simples.mp3"
    if os.path.exists(test_file):
        text = stt.transcribe(test_file)
        print(f"Resultado da transcrição: '{text}'")
