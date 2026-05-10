from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ProblemaPL(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class SignoValor(BaseModel):
    signo: str
    valor: float

class FuncionObjetivo(SignoValor):
    tipo: str

class ResumenProblema(ProblemaPL):
    id: str
    fecha_creacion: str

class Resultado(BaseModel):
    funcion_objetivo: str
    mensaje: Optional[str] = None

