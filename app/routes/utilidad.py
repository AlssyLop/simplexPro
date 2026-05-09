from fastapi import APIRouter, HTTPException, Response

from app.services.grafico import metodoGrafico
from app.validators.problema import validar_grafico, validar_simplex
from app.db.connection import DbDep
from app.schemas.problema import ProblemaPLCreate
from app.db import crud
from app.services.exportador import generar_pdf_grafico

router = APIRouter(tags=["Utilidad"])

@router.post("/validar")
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

@router.get("/problemas/{id}/exportar")
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
