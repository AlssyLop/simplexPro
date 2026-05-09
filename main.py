from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Annotated
import aiosqlite

from algoritmoPL import metodoGrafico, metodoSimplex
from controlador import validar_grafico, validar_simplex
from database import get_db, init_db
from schemas import (
    ProblemaPLCreate, 
    ProblemaPLResponse, 
    ResumenProblema, 
    ProblemaPLBase
)
import crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar base de datos si no existe
    await init_db()
    yield

app = FastAPI(title="SimplexPro API", lifespan=lifespan)

DbDep = Annotated[aiosqlite.Connection, Depends(get_db)]

# --- Endpoints de Resolución ---

@app.post("/grafico", tags=["Resolución"])
async def resolver_grafico(problema: ProblemaPLCreate):
    # Convertimos a dict para compatibilidad con algoritmo viejo
    problema_dict = problema.model_dump()
    validar_grafico(problema_dict)
    return metodoGrafico(problema_dict)

@app.post("/simplex", tags=["Resolución"])
async def resolver_simplex(problema: ProblemaPLCreate):
    problema_dict = problema.model_dump()
    validar_simplex(problema_dict)
    return metodoSimplex(problema_dict)

# --- CRUD de Problemas ---

@app.post("/problemas", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["CRUD"])
async def guardar_problema(problema: ProblemaPLCreate, db: DbDep):
    id_nuevo = await crud.create_problema(db, problema)
    return {"id": id_nuevo, "mensaje": "Problema guardado"}

@app.get("/problemas", response_model=List[ResumenProblema], tags=["CRUD"])
async def listar_problemas(db: DbDep):
    return await crud.get_problemas(db)

@app.put("/problemas/{id}", tags=["CRUD"])
async def actualizar_problema(id: str, problema: ProblemaPLCreate, db: DbDep):
    exito = await crud.update_problema(db, id, problema)
    if not exito:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return {"mensaje": "Problema actualizado"}

@app.delete("/problemas/{id}", tags=["CRUD"])
async def borrar_problema(id: str, db: DbDep):
    await crud.delete_problema(db, id)
    return {"mensaje": "Problema borrado"}

# --- Validación y Otros ---

@app.post("/validar", tags=["Utilidad"])
async def validar_problema(problema: ProblemaPLCreate):
    """Valida sin resolver, devuelve 200 si todo ok."""
    prob_dict = problema.model_dump()
    # Intentamos validar para ambos
    try:
        if len(prob_dict["variables"]) == 2:
            validar_grafico(prob_dict)
        validar_simplex(prob_dict)
        return {"mensaje": "Ok", "valido": True}
    except HTTPException as e:
        return {"mensaje": "Piedra rota", "valido": False, "errores": e.detail}

@app.get("/problemas/{id}/exportar", tags=["Utilidad"])
async def exportar_problema(id: str, db: DbDep):
    """Placeholder para exportar. Por ahora devuelve el JSON."""
    # Implementación básica para demostrar
    return {"mensaje": "Exportación a PDF próximamente", "id": id}
