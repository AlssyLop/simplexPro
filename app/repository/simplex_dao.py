import aiosqlite
import json
from app.schemas.simplex_model import ProblemaPL, Resultado
from app.repository.problemaPL_dao import registrar_problemaPL, registrar_variables, registrar_restricciones

async def guardar_resultado_simplex(db: aiosqlite.Connection, p: ProblemaPL, resultado: Resultado):
    
    problemaPL = (p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), resultado.funcion_objetivo)
    problema_id = await registrar_problemaPL(db, problemaPL)
    
    variables = [(var_key, var_nombre, problema_id) for var_key, var_nombre in p.variables.items()]
    await registrar_variables(db, variables)

    restricciones = [(problema_id, inecuacion(restr), restr.glosa) for restr in p.restricciones]
    await registrar_restricciones(db, restricciones)
    
    valor_fo = json.dumps(resultado.valor_fo)
    mensaje = resultado.mensaje
    cursor = await db.execute("INSERT INTO metodoSimple (problemaID, valorFo, mensaje) VALUES (?, ?, ?) RETURNING metodoSimpleID",(problema_id, valor_fo, mensaje))
    metodo_simple_id = await cursor.fetchone()[0]

    iteraciones = [(metodo_simple_id, i.iteracion, i.entra, i.sale, i.elementoPivote, i.razonMinima) for i in resultado.iteraciones]
    await db.executemany("INSERT INTO iteracionSimplex (metodoSimpleID, iteracion, entra, sale, elementoPivote, razonMinima) VALUES (?, ?, ?, ?, ?, ?)", iteraciones)
    await db.commit()

def inecuacion(restr):
    inecuacion = ""
    for key, value in restr.items():
        if key != "signo" and key != "valor" and key != "glosa":
            inecuacion += f"{value}{key} + "
    inecuacion = inecuacion.strip().rstrip('+').strip() + f" {restr.signo} {restr.valor}"
    return inecuacion