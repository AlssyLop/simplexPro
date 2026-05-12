from fastapi import APIRouter, HTTPException, status
from typing import List

from app.db.connection import DbDep
from app.schemas.grafico_model import MostrarResultadoGrafico
from app.schemas.simplex_model import MostrarResultadoSimplex
from app.validators.problema import validar_problema_grafico, validar_problema_simplex
from app.repository.grafico_dao import guardar_resultado_grafico, actualizar_resultado_grafico, mostrar_resultado_grafico
from app.repository.simplex_dao import guardar_resultado_simplex, mostrar_resultado_simplex, actualizar_resultado_simplex
from app.repository.problemaPL_dao import listar_problemas, existe_problema, eliminar_problema
from app.schemas.problemaPL_model import ResumenProblema
from app.services.grafico import metodoGrafico
from app.services.simplex import metodoSimplex
from app.schemas.grafico_model import ProblemaPL as ProblemaGrafico, Resultado as ResultadoGrafico
from app.schemas.simplex_model import ProblemaPL as ProblemaSimplex, Resultado as ResultadoSimplex

router = APIRouter(prefix="/problema", tags=["Problemas"])

@router.get("/listar", response_model=List[ResumenProblema], status_code=status.HTTP_200_OK)
async def obtener_problemas(db: DbDep, page: int = 1):
    return await listar_problemas(db, offset=(page-1)*10)

@router.get("/solucion/grafica/{id}", response_model=MostrarResultadoGrafico, status_code=status.HTTP_200_OK)
async def obtener_solucion_grafica(db: DbDep, id: str):
    resultado = await mostrar_resultado_grafico(db, id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return resultado

@router.get("/solucion/simplex/{id}", response_model=MostrarResultadoSimplex, status_code=status.HTTP_200_OK)
async def obtener_solucion_simplex(db: DbDep, id: str):
    resultado = await mostrar_resultado_simplex(db, id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    return resultado

@router.post("/registrar", response_model=dict, status_code=status.HTTP_201_CREATED)
async def registrar(metodo: str, problema: dict, db: DbDep):
    if metodo == "grafico":
        validar_problema_grafico(problema)
        p = ProblemaGrafico(**problema)
        res = metodoGrafico(p)
        id = await guardar_resultado_grafico(db, p, res)
    elif metodo == "simplex":
        validar_problema_simplex(problema)
        p = ProblemaSimplex(**problema)
        res_dict = metodoSimplex(p)
        res = ResultadoSimplex(**res_dict)
        id = await guardar_resultado_simplex(db, p, res)
    else:
        raise HTTPException(status_code=400, detail="Metodo no valido")
    return {"id": id}

@router.put("/actualizar", response_model=dict, status_code=status.HTTP_200_OK)
async def actualizar(metodo: str, problema: dict, db: DbDep):
    problema_id = problema.get("problemaID") or problema.get("id")
    if not problema_id:
        raise HTTPException(status_code=400, detail="Falta el ID del problema para actualizar")

    if metodo == "grafico":
        validar_problema_grafico(problema)
        p = ProblemaGrafico(**problema)
        res = metodoGrafico(p)
        await actualizar_resultado_grafico(db, problema_id, res)
    elif metodo == "simplex":
        validar_problema_simplex(problema)
        p = ProblemaSimplex(**problema)
        res_dict = metodoSimplex(p)
        res = ResultadoSimplex(**res_dict)
        await actualizar_resultado_simplex(db, problema_id, res)
    else:   
        raise HTTPException(status_code=400, detail="Metodo no valido")
    return {"mensaje": "Problema actualizado"}

@router.delete("/eliminar/{id}", response_model=dict, status_code=status.HTTP_200_OK)
async def borrar_problema(id: str, db: DbDep):
    if await eliminar_problema(db, id):
        return {"mensaje": "Problema eliminado"}
    raise HTTPException(status_code=404, detail="Problema no encontrado")
