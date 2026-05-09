from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from typing import List, Annotated
import aiosqlite
import json

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
from exportador import generar_pdf_grafico

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar base de datos si no existe
    await init_db()
    yield

app = FastAPI(title="SimplexPro API", lifespan=lifespan)

DbDep = Annotated[aiosqlite.Connection, Depends(get_db)]

# --- Endpoints de Resolución ---

@app.post("/grafico", tags=["Resolución"])
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

@app.post("/simplex", tags=["Resolución"])
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
        return {"status": "Ok"}
    except HTTPException as e:
        return {"mensaje": "El problema no es valido", "status": "Error"}

@app.get("/problemas/{id}/exportar", tags=["Utilidad"])
async def exportar_problema(id: str, db: DbDep):
    """Genera un reporte PDF con la solución gráfica del problema."""
    # 1. Obtener datos completos de la base de datos
    problema_dict = await crud.get_problema_completo(db, id)
    if not problema_dict:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    
    # 2. Si el problema tiene 2 variables, podemos usar el método gráfico
    if len(problema_dict["variables"]) != 2:
        raise HTTPException(status_code=400, detail="La exportación a PDF solo está soportada para problemas de 2 variables (Método Gráfico)")
    
    try:
        validar_grafico(problema_dict)
        resultados_grafico = metodoGrafico(problema_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al resolver el problema: {str(e)}")

    # 3. Generar PDF
    try:
        pdf_bytes = generar_pdf_grafico(problema_dict, resultados_grafico)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_problema_{id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")
