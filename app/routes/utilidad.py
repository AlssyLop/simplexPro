from fastapi import APIRouter, HTTPException, Response
from app.db.connection import DbDep
from app.repository.grafico_dao import mostrar_resultado_grafico
from app.services.exportador import generar_pdf_grafico

router = APIRouter(tags=["Utilidad"])

@router.get("/problemas/{id}/exportar", response_class=Response)
async def exportar_problema(id: str, db: DbDep):
    """Genera un reporte PDF con la solución gráfica del problema."""
    resultado = await mostrar_resultado_grafico(db, id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    
    try:
        pdf_bytes = generar_pdf_grafico(resultado)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_problema_{id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")
