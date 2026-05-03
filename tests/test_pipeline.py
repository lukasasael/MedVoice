import pytest
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
