from fastapi import APIRouter, HTTPException, status
from typing import List

from app.db.connection import DbDep
from app.validators.problema import validar_problema_grafico, validar_problema_simplex
from app.repository.grafico_dao import guardar_resultado_grafico, actualizar_resultado_grafico, mostrar_resultado_grafico
from app.repository.simplex_dao import guardar_resultado_simplex, mostrar_resultado_simplex, actualizar_resultado_simplex
from app.repository.problemaPL_dao import listar_problemas, existe_problema, eliminar_problema
from app.services.grafico import metodoGrafico
from app.services.simplex import metodoSimplex
from app.schemas.problemaPL import ProblemaPL
from app.schemas.resultados import ResultadoGrafico, ResultadoSimplex, MostrarResultadoGrafico, MostrarResultadoSimplex, ListaResumenProblemas

router = APIRouter(prefix="/problemas", tags=["Problemas"])

@router.get("", response_model=ListaResumenProblemas, status_code=status.HTTP_200_OK, description="Muestra un listado paginado de los problemas registrados")
async def obtener_problemas(db: DbDep, page: int = 1):
    if page < 1:
        raise HTTPException(status_code=400, detail="Pagina no valida")
    return await listar_problemas(db, offset=(page-1)*10)

@router.get("/{id}/grafica", response_model=MostrarResultadoGrafico, status_code=status.HTTP_200_OK, description="Obtener solucion grafica")
async def obtener_solucion_grafica(db: DbDep, id: str):
    resultado = await mostrar_resultado_grafico(db, id)
    if not resultado:
        print(resultado)
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return resultado

@router.get("/{id}/simplex", response_model=MostrarResultadoSimplex, status_code=status.HTTP_200_OK, description="Obtener solucion simplex")
async def obtener_solucion_simplex(db: DbDep, id: str):
    resultado = await mostrar_resultado_simplex(db, id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return resultado

@router.post("/registrar", response_model=dict, status_code=status.HTTP_201_CREATED, description="Registra un nuevo problema")
async def registrar(metodo: str, problema: dict, db: DbDep):
    if metodo == "grafico":
        validar_problema_grafico(problema)
        p = ProblemaPL(**problema)
        res = metodoGrafico(p)
        id = await guardar_resultado_grafico(db, p, res)
    elif metodo == "simplex":
        validar_problema_simplex(problema)
        p = ProblemaPL(**problema)
        res = metodoSimplex(p)
        id = await guardar_resultado_simplex(db, p, res)
    else:
        raise HTTPException(status_code=400, detail="Metodo no valido")
    return {"id": id}

@router.put("/actualizar", response_model=dict, status_code=status.HTTP_200_OK, description="Actualiza un problema")
async def actualizar(metodo: str, id: str, problema: dict, db: DbDep):

    if metodo not in ["grafico", "simplex"]:
        raise HTTPException(status_code=400, detail="Metodo no valido")

    if not await existe_problema(db, id):
        raise HTTPException(status_code=404, detail="Problema no encontrado")

    if metodo == "grafico":
        validar_problema_grafico(problema)
        p = ProblemaPL(**problema)
        res = metodoGrafico(p)
        await actualizar_resultado_grafico(db, id, res)
    else:
        validar_problema_simplex(problema)
        p = ProblemaPL(**problema)
        res = metodoSimplex(p)
        await actualizar_resultado_simplex(db, id, res)
        
    return {"mensaje": "Problema actualizado"}

@router.delete("/eliminar/{id}", response_model=dict, status_code=status.HTTP_200_OK, description="Elimina un problema registrado")
async def borrar_problema(id: str, db: DbDep):
    if await eliminar_problema(db, id):
        return {"mensaje": "Problema eliminado"}
    raise HTTPException(status_code=404, detail="Problema no encontrado")
