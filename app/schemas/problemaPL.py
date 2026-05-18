from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal

class TituloDescripcion(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class Variables(BaseModel):
    x: Optional[float] = 0.0
    y: Optional[float] = 0.0

class Restriccion(Variables):
    terminos: Optional[Dict[str, float]] = None
    signo: Literal["<=", "<", ">=", ">", "="]
    constante: float
    glosa: Optional[str] = None

class FuncionObjetivo(Variables):
    tipo: Literal["max", "min"]
    terminos: Optional[Dict[str, float]] = None

class ProblemaPL(TituloDescripcion):
    x: Optional[str] = "x"
    y: Optional[str] = "y"
    variables: Dict[str, str]
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo
