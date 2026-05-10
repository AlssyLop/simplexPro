from pydantic import BaseModel
from typing import Dict, List, Optional
from ..schemas.problemaPL_model import ProblemaPL, FuncionObjetivo, SignoValor, Resultado

class Variables(BaseModel):
    x: str
    y: str

class Restriccion(SignoValor):
    x: float
    y: float
    glosa: Optional[str] = None

class FuncionObjetivo(FuncionObjetivo):
    x: float
    y: float
    
class ProblemaPL(ProblemaPL):
    variables: Variables
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo

class Resultado(Resultado):
    valores_fo: List[str]
    img: str