from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple, Union
from app.schemas.problemaPL import TituloDescripcion

class ResumenProblema(TituloDescripcion):
    id:str
    tipoOptimizacion: str
    metodo: Optional[str] = None
    fechaCreacion: str

class FuncionObjetivo(BaseModel):
    funcion_objetivo:str
    mensaje: str

class ResultadoGrafico(FuncionObjetivo):
    valoresFO: List[str]
    grafico: str

class Iteracion(BaseModel):
    iteracion: int
    entra: str
    sale: str
    razonMinima: Union[float, str, None]
    elementoPivote: Union[float, str, None]
    tabla: Dict[str, List[Union[float, str, None, int]]]

class ResultadoSimplex(FuncionObjetivo):
    valorFO: str
    iteraciones: List[Iteracion]

class InecuacionGlosa(BaseModel):
    inecuacion: str
    glosa: Optional[str] = None

class MostrarResultadoGrafico(ResumenProblema, ResultadoGrafico):
    variables: Dict[str, str]
    restricciones: List[InecuacionGlosa]

class MostrarResultadoSimplex(ResumenProblema, ResultadoSimplex):
    variables: Dict[str, str]
    restricciones: List[InecuacionGlosa]