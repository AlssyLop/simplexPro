from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class Variable(BaseModel):
    nombre: str

class RestriccionTermino(BaseModel):
    variable: str
    coeficiente: float

class Restriccion(BaseModel):
    x: float
    y: float
    signo: str
    valor: float
    glosa: Optional[str] = None

class FuncionObjetivo(BaseModel):
    x: float
    y: float
    tipo: str

class ProblemaPLBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    variables: Dict[str, str]
    restricciones: List[Restriccion]
    funcion_objetivo: FuncionObjetivo

class ProblemaPLCreate(ProblemaPLBase):
    pass

class ProblemaPLResponse(ProblemaPLBase):
    id: str
    fecha_creacion: str

class ResumenProblema(BaseModel):
    id: str
    titulo: str
    fecha_creacion: str
