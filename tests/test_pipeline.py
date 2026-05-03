import pytest
from unittest.mock import patch
from pydantic import ValidationError
from src.llm_extractor import LLMExtractor

@pytest.fixture
def extractor():
    return LLMExtractor()

def test_caso_valido_simples(extractor):
    text = "ajustar a frequência para cinco hertz"
    res = extractor.extract_hybrid(text)
    assert res.intent == "ajustar_parametro"
    assert res.parameter == "frequencia"
    assert res.value == 5.0
    assert res.unit == "Hz"

def test_caso_unidade_omitida(extractor):
    text = "coloca a temperatura em trinta e seis"
    res = extractor.extract_hybrid(text)
    assert res.intent == "ajustar_parametro"
    assert res.parameter == "temperatura"
    assert res.value == 36.0

def test_caso_incompleto(extractor):
    text = "ajustar a pressão para"
    res = extractor.extract_hybrid(text)
    assert res.status in ["INCOMPLETO", "AMBIGUO"]

def test_caso_invalido(extractor):
    text = "preparar café expresso"
    res = extractor.extract_hybrid(text)
    assert res.intent == "desconhecido"
    assert res.parameter == "nenhum"

def test_caso_ambiguo(extractor):
    text = "aumenta aquilo lá para dez"
    res = extractor.extract_hybrid(text)
    # The LLM should recognize it's an adjustment, but the parameter is ambiguous
    assert res.parameter == "nenhum"
    assert res.status in ["AMBIGUO", "INCOMPLETO"]

@patch("src.llm_extractor.Groq")
def test_falha_parser(mock_groq):
    # Setup mock to return invalid JSON (missing quotes or wrong types)
    mock_client_instance = mock_groq.return_value
    mock_chat_completion = mock_client_instance.chat.completions.create.return_value
    
    # Simulate the LLM returning a JSON that violates the Pydantic schema (e.g. wrong type for 'intent')
    class MockMessage:
        content = '{"intent": "intent_inexistente", "parameter": "frequencia", "status": "OK", "requires_confirmation": false, "validation_errors": [], "notes": ""}'
        
    class MockChoice:
        message = MockMessage()
        
    mock_chat_completion.choices = [MockChoice()]
    
    # Temporarily replace the extractor's client
    extractor = LLMExtractor()
    extractor.client = mock_client_instance
    
    # It should raise a ValidationError because "intent_inexistente" is not in IntentEnum
    with pytest.raises(ValidationError):
        extractor.extract_pure("texto qualquer")
