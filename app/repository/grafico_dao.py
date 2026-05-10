import aiosqlite
import json
import base64
from app.schemas.grafico_model import ProblemaPL, Resultado
from app.repository.problemaPL_dao import post_problemaPL, post_variables, post_restricciones

async def guardar_resultado_grafico(db: aiosqlite.Connection, p: ProblemaPL, resultado: Resultado):

    problemaPL = (p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), resultado.funcion_objetivo)
    problema_id = await post_problemaPL(db, problemaPL)
    
    variables = [('x', p.variables.x, problema_id), ('y', p.variables.y, problema_id)]
    await post_variables(db, variables)

    restricciones = []
    for restr in p.restricciones:
        inecuacion = f"{restr.x}x + {restr.y}y {restr.signo} {restr.valor}"
        restricciones.append((problema_id, inecuacion, restr.glosa))
    await post_restricciones(db, restricciones)
    
    grafico_b64 = resultado.img
    if "," in grafico_b64:
        grafico_b64 = grafico_b64.split(",")[1]
    grafico_bytes = base64.b64decode(grafico_b64)
    valores_fo = json.dumps(resultado.valores_fo)
    mensaje = resultado.mensaje
    await db.execute(
        "INSERT INTO metodoGrafico (problemaID, valoresFO, mensaje, grafico) VALUES (?, ?, ?, ?)",
        (problema_id, valores_fo, mensaje, grafico_bytes)
    )
    await db.commit()