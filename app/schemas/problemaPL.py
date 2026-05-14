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

class ListaTerminos(BaseModel):
    lista_terminos: Optional[List[Termino]] = None

class Restriccion(Variables, ListaTerminos):
    signo: Literal["<=", "<", ">=", ">", "="]
    constante: float
    glosa: Optional[str] = None

class FuncionObjetivo(Variables, ListaTerminos):
    tipo: Literal["max", "min"]

class ProblemaPL(TituloDescripcion):
    x: Optional[str] = "x"
    y: Optional[str] = "y"
    variables: Dict[str, str]
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo
