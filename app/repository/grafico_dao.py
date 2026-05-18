import aiosqlite
import json
import base64
from app.repository.problemaPL_dao import registrar_problema, registrar_variables, registrar_restricciones, actualizar_problema
from app.schemas.problemaPL import ProblemaPL
from app.schemas.resultados import ResultadoGrafico, MostrarResultadoGrafico

async def guardar_resultado_grafico(db: aiosqlite.Connection, p: ProblemaPL, resultado: ResultadoGrafico):

    problemaPL = (
        p.titulo, 
        p.descripcion, 
        p.funcion_objetivo.tipo.upper(), 
        resultado.funcion_objetivo,
        "Grafico"
    )
    problema_id = await registrar_problema(db, problemaPL)
    await registrar_variables(db, problema_id, p.variables)
    await registrar_restricciones(db, problema_id, p.restricciones)
    
    grafico_b64 = resultado.grafico
    if "," in grafico_b64:
        grafico_b64 = grafico_b64.split(",")[1]
    grafico_bytes = base64.b64decode(grafico_b64)
    valores_fo = json.dumps(resultado.valoresFO)
    mensaje = resultado.mensaje
    await db.execute(
        "INSERT INTO metodoGrafico (problemaID, valoresFO, mensaje, grafico) VALUES (?, ?, ?, ?)",
        (problema_id, valores_fo, mensaje, grafico_bytes)
    )
    await db.commit()
    return problema_id


async def mostrar_resultado_grafico(db: aiosqlite.Connection, id: str) -> MostrarResultadoGrafico:
    query = """
        SELECT
            p.problemaID,
            p.titulo,
            p.descripcion,
            p.tipoOptimizacion,
            p.funcionObjetivo,
            p.fechaCreacion,
            mg.valoresFO,
            mg.mensaje,
            mg.grafico,
            (SELECT json_group_object(variable, nombre) FROM variables WHERE problemaID = p.problemaID ORDER BY fechaCreacion ASC) as variables_json,
            (SELECT json_group_array(
                json_object('inecuacion', r.inecuacion, 'glosa', r.glosa)
            ) FROM restricciones r WHERE r.problemaID = p.problemaID ORDER BY r.fechaCreacion ASC) as restricciones_json
        FROM problemaPL p
        JOIN metodoGrafico mg ON p.problemaID = mg.problemaID
        WHERE p.problemaID = ?
    """

    cursor = await db.execute(query, (id,))
    resultado = await cursor.fetchone()
    
    if resultado:
        return MostrarResultadoGrafico(
            id = resultado[0],
            titulo = resultado[1],
            descripcion = resultado[2],
            tipoOptimizacion = resultado[3],
            funcion_objetivo = resultado[4],
            fechaCreacion = resultado[5],
            valoresFO = json.loads(resultado[6]),
            mensaje = resultado[7],
            grafico = base64.b64encode(resultado[8]).decode("utf-8"),
            variables = json.loads(resultado[9]),
            restricciones = json.loads(resultado[10]),
        )
    return None

 
async def actualizar_resultado_grafico(db: aiosqlite.Connection, problema_id: str, p: ProblemaPL, resultado: ResultadoGrafico):
    """
    Actualiza el resultado de un problema de método gráfico.
    """
    problemaPL = (
        p.titulo, 
        p.descripcion, 
        p.funcion_objetivo.tipo.upper(), 
        resultado.funcion_objetivo,
        problema_id
    )
    await actualizar_problema(db, problemaPL)
    
    grafico_b64 = resultado.grafico
    if "," in grafico_b64:
        grafico_b64 = grafico_b64.split(",")[1]
    grafico_bytes = base64.b64decode(grafico_b64)
    valores_fo = json.dumps(resultado.valoresFO)
    mensaje = resultado.mensaje
    await db.execute(
        "UPDATE metodoGrafico SET valoresFO = ?, mensaje = ?, grafico = ? WHERE problemaID = ?",
        (valores_fo, mensaje, grafico_bytes, problema_id)
    )
    await db.commit()
    