from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal

class TituloDescripcion(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class Variables(BaseModel):
    x: Optional[float] = 0.0
    y: Optional[float] = 0.0

class Termino(BaseModel):
    coeficiente: float
    variable: str

class Restriccion(Variables):
    terminos: Optional[List[Termino]] = None
    signo: Literal["<=", "<", ">=", ">"]
    constante: float
    glosa: Optional[str] = None

class FuncionObjetivo(Variables):
    terminos: Optional[List[Termino]] = None
    tipo: Literal["max", "min"]

class ProblemaPL(TituloDescripcion):
    x: Optional[str] = "x"
    y: Optional[str] = "y"
    variables: Dict[str, str]
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo
