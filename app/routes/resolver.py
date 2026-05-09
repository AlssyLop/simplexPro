from fastapi import APIRouter

from app.services.grafico import metodoGrafico
from app.services.simplex import metodoSimplex
from app.validators.problema import validar_grafico, validar_simplex
from app.db.connection import DbDep
from app.schemas.problema import ProblemaPLCreate
from app.db import crud

router = APIRouter(tags=["Resolución"])

@router.post("/grafico")
async def resolver_grafico(problema: ProblemaPLCreate, db: DbDep):
    problema_dict = problema.model_dump()
    validar_grafico(problema_dict)
    
    # 1. Guardar problema atómicamente y obtener ID
    id_problema = await crud.create_problema(db, problema)
    
    # 2. Resolver
    resultado = metodoGrafico(problema_dict)
    
    # 3. Guardar resultado
    await crud.save_resultado_grafico(db, id_problema, resultado)
    
    # 4. Adjuntar ID al resultado
    resultado["id_problema"] = id_problema
    return resultado

@router.post("/simplex")
async def resolver_simplex(problema: ProblemaPLCreate, db: DbDep):
    problema_dict = problema.model_dump()
    validar_simplex(problema_dict)
    
    # 1. Guardar problema atómicamente y obtener ID
    id_problema = await crud.create_problema(db, problema)
    
    # 2. Resolver
    resultado = metodoSimplex(problema_dict)
    
    # 3. Guardar resultado
    await crud.save_resultado_simplex(db, id_problema, resultado)
    
    # 4. Adjuntar ID al resultado
    resultado["id_problema"] = id_problema
    return resultado
