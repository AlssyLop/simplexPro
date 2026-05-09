from fastapi import APIRouter, HTTPException, status
from typing import List

from app.db.connection import DbDep
from app.schemas.problema import ProblemaPLCreate, ResumenProblema
from app.db import crud

router = APIRouter(prefix="/problemas", tags=["CRUD"])

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def guardar_problema(problema: ProblemaPLCreate, db: DbDep):
    id_nuevo = await crud.create_problema(db, problema)
    return {"id": id_nuevo, "mensaje": "Problema guardado"}

@router.get("", response_model=List[ResumenProblema])
async def listar_problemas(db: DbDep):
    return await crud.get_problemas(db)

@router.put("/{id}")
async def actualizar_problema(id: str, problema: ProblemaPLCreate, db: DbDep):
    exito = await crud.update_problema(db, id, problema)
    if not exito:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return {"mensaje": "Problema actualizado"}

@router.delete("/{id}")
async def borrar_problema(id: str, db: DbDep):
    await crud.delete_problema(db, id)
    return {"mensaje": "Problema borrado"}
