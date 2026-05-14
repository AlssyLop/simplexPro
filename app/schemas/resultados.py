from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from app.schemas.problemaPL import TituloDescripcion

class ResumenProblema(TituloDescripcion):
    id:str
    tipoOptimizacion: str
    fechaCreacion: str

class ListaResumenProblemas(BaseModel):
    problemas: List[ResumenProblema]

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
    razonMinima: float
    elementoPivote: float
    tabla: Dict[str, List[str]]

class ResultadoSimplex(FuncionObjetivo):
    valorFO: str
    iteraciones: List[Iteracion]

class InecuacionGlosa(BaseModel):
    inecuacion: str
    glosa: str

class MostrarResultadoGrafico(ResumenProblema, ResultadoGrafico):
    variables: Dict[str, str]
    restricciones: List[InecuacionGlosa]

class MostrarResultadoSimplex(ResumenProblema, ResultadoSimplex):
    variables: Dict[str, str]
    restricciones: List[InecuacionGlosa]