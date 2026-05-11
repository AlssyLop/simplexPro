from pydantic import BaseModel
from typing import Dict, List, Optional
from ..schemas.problemaPL_model import ProblemaPL, FuncionObjetivo, ResumenProblema, SignoValor, Resultado

class Variables(BaseModel):
    x: str
    y: str

class Restriccion(SignoValor):
    x: float
    y: float
    glosa: Optional[str] = None

class FuncionObjetivo(BaseModel):
    x: float
    y: float
    tipo: str
    
class ProblemaPL(ProblemaPL):
    variables: Variables
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo

class Resultado(Resultado):
    valoresFO: List[str]
    grafico: str

class Inecuacion(BaseModel):
    inecuacion: str
    glosa: Optional[str] = None

class MostrarResultadoGrafico(ResumenProblema, Resultado):
    variables: Variables
    restricciones: List[Inecuacion]