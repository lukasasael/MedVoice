import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json

from dotenv import load_dotenv
from groq import Groq

from src.schema import CommandExtraction

load_dotenv()


class LLMExtractor:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não configurada no ambiente ou .env.")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def extract_pure(self, text: str) -> CommandExtraction:
        """
        Variante A: Extração pura usando LLM e Structured Outputs JSON via Prompt Engineering.
        """
        schema_json = CommandExtraction.model_json_schema()

        prompt = f"""
        Você é um sistema de IA integrado a um equipamento médico.
        Analise a transcrição de voz do usuário e extraia as entidades estritamente de acordo com o JSON schema fornecido.
        Seja robusto a pequenos erros de transcrição do Speech-to-Text (ex: 'rertz' em vez de 'hertz').
        Responda APENAS com um objeto JSON válido, sem comentários ou formatação Markdown.

        Texto transcrito: "{text}"

        Schema JSON (Pydantic):
        {json.dumps(schema_json, indent=2)}
        """

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON extractor. Output strictly valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            model=self.model_name,
            temperature=0,
            response_format={"type": "json_object"},
        )

        response_json = json.loads(chat_completion.choices[0].message.content)
        return CommandExtraction(**response_json)

    def extract_hybrid(self, text: str) -> CommandExtraction:
        """
        Variante B: Abordagem híbrida (LLM + Pós-processamento Baseado em Regras Determinísticas).
        """
        extraction = self.extract_pure(text)

        # Pós-processamento e Normalização (Regras)
        if extraction.unit:
            unit_lower = extraction.unit.lower().strip()
            # Normalizar frequencia
            if unit_lower in ["hertz", "hzs", "rertz", "hz", "heats"]:
                extraction.unit = "Hz"
            # Normalizar temperatura
            elif unit_lower in ["graus", "celsius", "graus celsius"]:
                extraction.unit = "°C"
            # Normalizar pressao e fluxo (simplificado)
            elif unit_lower in ["litros", "litro", "l"]:
                extraction.unit = "L"

        # Validação semântica adicional de completude
        if extraction.intent == "ajustar_parametro" and extraction.value is None:
            if extraction.status != "INCOMPLETO":
                extraction.status = "INCOMPLETO"
                extraction.validation_errors.append("Valor alvo ausente para intenção de ajuste.")

        return extraction


if __name__ == "__main__":
    extractor = LLMExtractor()
    text = "ajusta a frequência pra dez hertz"
    print(f"Texto: {text}")
    print("\n--- Variante A ---")
    print(extractor.extract_pure(text).model_dump_json(indent=2))

    print("\n--- Variante B ---")
    text2 = "coloca a temperatura em trinta graus"
    print(extractor.extract_hybrid(text2).model_dump_json(indent=2))
