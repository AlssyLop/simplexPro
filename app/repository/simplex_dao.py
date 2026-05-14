import aiosqlite
import json
from app.repository.problemaPL_dao import registrar_problema, registrar_variables, registrar_restricciones, actualizar_problema
from typing import Optional
from app.schemas.problemaPL import ProblemaPL
from app.schemas.resultados import ResultadoSimplex, MostrarResultadoSimplex, Iteracion

async def guardar_resultado_simplex(db: aiosqlite.Connection, p: ProblemaPL, resultado: ResultadoSimplex):
    
    problemaPL = (p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), resultado.funcion_objetivo)
    problema_id = await registrar_problema(db, problemaPL)
    
    await registrar_variables(db, problema_id, p.variables)
    await registrar_restricciones(db, problema_id, p.restricciones)
    
    valor_fo = json.dumps(resultado.valorFO)
    mensaje = resultado.mensaje
    cursor = await db.execute("INSERT INTO metodoSimple (problemaID, valorFo, mensaje) VALUES (?, ?, ?) RETURNING metodoSimpleID",(problema_id, valor_fo, mensaje))
    row = await cursor.fetchone()
    metodo_simple_id = row[0]

    iteraciones = [(metodo_simple_id, i.iteracion, i.entra, i.sale, i.elementoPivote, i.razonMinima, json.dumps(i.tabla)) for i in resultado.iteraciones]
    await db.executemany("INSERT INTO iteracionSimple (metodoSimpleID, iteracion, entra, sale, elementoPivote, razonMinima, tabla) VALUES (?, ?, ?, ?, ?, ?, ?)", iteraciones)
    await db.commit()
    return problema_id

def inecuacion(restr):
    inecuacion = ""
    for key, value in restr.items():
        if key != "signo" and key != "valor" and key != "glosa":
            inecuacion += f"{value}{key} + "
    inecuacion = inecuacion.strip().rstrip('+').strip() + f" {restr['signo']} {restr['valor']}"
    return inecuacion

async def mostrar_resultado_simplex(db: aiosqlite.Connection, id: str) -> Optional[MostrarResultadoSimplex]:
    query = """
        SELECT 
            p.titulo, 
            p.descripcion, 
            p.tipoOptimizacion, 
            p.funcionObjetivo,
            ms.valorFo,
            ms.mensaje,
            ms.metodoSimpleID,
            (SELECT json_group_object(variable, nombre) FROM variables WHERE problemaID = p.problemaID ORDER BY fechaCreacion ASC) as variables_json,
            (SELECT json_group_array(
                json_object("inecuacion", r.inecuacion, "glosa", r.glosa)
            ) FROM restricciones r WHERE r.problemaID = p.problemaID ORDER BY r.fechaCreacion ASC) as restricciones_json,
            p.fechaCreacion
        FROM problemaPL p
        JOIN metodoSimple ms ON p.problemaID = ms.problemaID
        WHERE p.problemaID = ?
    """
    cursor = await db.execute(query, (id,))
    resultado = await cursor.fetchone()
    
    if not resultado:
        return None
        
    metodo_simple_id = resultado[6]
    iter_query = """
        SELECT iteracion, entra, sale, razonMinima, elementoPivote, tabla
        FROM iteracionSimple
        WHERE metodoSimpleID = ?
        ORDER BY iteracion ASC
    """
    cursor = await db.execute(iter_query, (metodo_simple_id,))
    iter_rows = await cursor.fetchall()
    
    iteraciones = []
    for row in iter_rows:
        iteraciones.append(Iteracion(
            iteracion=row[0],
            entra=row[1],
            sale=row[2],
            razonMinima=row[3],
            elementoPivote=row[4],
            tabla=json.loads(row[5]) if row[5] else {}
        ))
        
    return MostrarResultadoSimplex(
        id = id,
        titulo = resultado[0],
        descripcion = resultado[1],
        variables = json.loads(resultado[7]),
        restricciones = json.loads(resultado[8]),
        funcion_objetivo = resultado[3],
        tipoOptimizacion = resultado[2],
        valorFO = json.loads(resultado[4]) if resultado[4].startswith('"') else resultado[4],
        mensaje = resultado[5],
        iteraciones = iteraciones,
        fechaCreacion = resultado[9]
    )

async def actualizar_resultado_simplex(db: aiosqlite.Connection, problema_id: str, resultado: ResultadoSimplex):
    valorFo = json.dumps(resultado.valorFO)
    mensaje = resultado.mensaje
    
    # 1. Update metodoSimple
    cursor = await db.execute(
        "UPDATE metodoSimple SET valorFo = ?, mensaje = ? WHERE problemaID = ? RETURNING metodoSimpleID",
        (valor_fo, mensaje, problema_id)
    )
    res = await cursor.fetchone()
    if not res:
        return # Problem not found
    
    metodo_simple_id = res[0]
    
    # 2. Delete old iterations
    await db.execute("DELETE FROM iteracionSimple WHERE metodoSimpleID = ?", (metodo_simple_id,))
    
    # 3. Insert new iterations
    iteraciones = [(metodo_simple_id, i.iteracion, i.entra, i.sale, i.elementoPivote, i.razonMinima, json.dumps(i.tabla)) for i in resultado.iteraciones]
    await db.executemany("INSERT INTO iteracionSimple (metodoSimpleID, iteracion, entra, sale, elementoPivote, razonMinima, tabla) VALUES (?, ?, ?, ?, ?, ?, ?)", iteraciones)
    
    await db.commit()