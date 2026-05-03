from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class IntentEnum(str, Enum):
    AJUSTAR_PARAMETRO = "ajustar_parametro"
    CONSULTAR_STATUS = "consultar_status"
    LIGAR_EQUIPAMENTO = "ligar_equipamento"
    DESLIGAR_EQUIPAMENTO = "desligar_equipamento"
    DESCONHECIDO = "desconhecido"

class ParameterEnum(str, Enum):
    FREQUENCIA = "frequencia"
    TEMPERATURA = "temperatura"
    PRESSAO = "pressao"
    FLUXO = "fluxo"
    VOLUME = "volume"
    NENHUM = "nenhum"

class StatusEnum(str, Enum):
    OK = "OK"
    AMBIGUO = "AMBIGUO"
    INCOMPLETO = "INCOMPLETO"
    INVALIDO = "INVALIDO"

class CommandExtraction(BaseModel):
    intent: IntentEnum = Field(description="A intenção principal do comando.")
    parameter: ParameterEnum = Field(description="O parâmetro do equipamento a ser ajustado ou consultado. Use 'nenhum' se não for mencionado um equipamento médico válido.")
    value: Optional[float] = Field(default=None, description="O valor numérico a ser ajustado. Nulo se não mencionado.")
    unit: Optional[str] = Field(default=None, description="A unidade de medida mencionada (ex: Hz, graus, litros). Nulo se não mencionada explicitamente.")
    status: StatusEnum = Field(description="O status da extração baseado na completude e clareza do comando. Se a intenção ou o parâmetro não estiverem claros, use AMBIGUO ou INCOMPLETO. Se pedir algo perigoso, INVALIDO.")
    requires_confirmation: bool = Field(description="Verdadeiro se for uma ação destrutiva ou alteração de parâmetro. Falso para consultas simples.")
    validation_errors: List[str] = Field(default_factory=list, description="Lista de erros semânticos ou valores ausentes críticos observados.")
    notes: str = Field(description="Breve explicação da extração e quaisquer ambiguidades encontradas no texto original.")
