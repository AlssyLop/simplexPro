from pydantic import BaseModel
from typing import Dict, List, Optional
from ..schemas.problemaPL_model import ProblemaPL, FuncionObjetivo, SignoValor, Resultado, ResumenProblema

class Variables(BaseModel):
    variables: Dict[str, float]

class Restriccion(SignoValor, Variables):
    pass

class FuncionObjetivo(FuncionObjetivo, Variables):
    pass

class ProblemaPL(ProblemaPL, BaseModel):
    variables: Dict[str, str]
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo

class Iteracion(BaseModel):
    iteracion: int
    entra: str
    sale: str
    razonMinima: float
    elementoPivote: float
    tabla: Dict[str, List[str]]

class Resultado(Resultado, BaseModel):
    valor_fo: str
    iteraciones: List[Iteracion]

class Inecuacion(BaseModel):
    inecuacion: str
    glosa: Optional[str] = None

class MostrarResultadoSimplex(ResumenProblema, Resultado):
    variables: Dict[str, str]
    restricciones: List[Inecuacion]