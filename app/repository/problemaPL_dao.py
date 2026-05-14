import aiosqlite
import json
from app.schemas.resultados import ListaResumenProblemas

async def existe_problema(db, problemaID):
    """
    Verifica si existe un problema con el ID dado.
    """
    cursor = await db.execute(
        "SELECT 1 FROM problemaPL WHERE problemaID = ? limit 1",
        (problemaID,)
    )
    res = await cursor.fetchone() is not None
    return res

async def registrar_problema(db, problemaPL):
    cursor = await db.execute(
        "INSERT INTO problemaPL (titulo, descripcion, tipoOptimizacion, funcionObjetivo) VALUES (?, ?, ?, ?) RETURNING problemaID",
        problemaPL
    )
    row = await cursor.fetchone()
    await db.commit()
    return row[0]

async def registrar_variables(db, problema_id, variables):
    variables_list = []
    for variable, nombre in variables.items():
        variables_list.append((variable, nombre, problema_id))
        
    await db.executemany(
        "INSERT INTO variables (variable, nombre, problemaID) VALUES (?, ?, ?)",
        variables_list
    )
    await db.commit()

async def registrar_restricciones(db, problema_id, restricciones):
    restricciones_list = []
    for restr in restricciones:
        inecuacion = ""
        for termino in restr.terminos:
            inecuacion += f"{termino.coeficiente}{termino.variable} + "
        inecuacion = inecuacion[:-2] + f" {restr.signo} {restr.constante}"
        restricciones_list.append((problema_id, inecuacion, restr.glosa))
        
    await db.executemany(
        "INSERT INTO restricciones (problemaID, inecuacion, glosa) VALUES (?, ?, ?)",
        restricciones_list
    )
    await db.commit()

async def listar_problemas(db: aiosqlite.Connection, offset: int):
    cursor = await db.execute(
        "SELECT json_group_array(json_object('id', problemaID, 'tipoOptimizacion', tipoOptimizacion, 'titulo', titulo, 'descripcion', descripcion, 'fechaCreacion', fechaCreacion)) FROM problemaPL LIMIT 10 OFFSET ?",
        (offset,)
    )
    lista_problemasPL = await cursor.fetchone()
    
    if lista_problemasPL is None:
        return ListaResumenProblemas(problemas=[])
    
    problemas = json.loads(lista_problemasPL[0])
    return ListaResumenProblemas(problemas=problemas)

async def actualizar_problema(db: aiosqlite.Connection, problemaPL):
    await db.execute(
        "UPDATE problemaPL SET titulo = ?, descripcion = ?, tipoOptimizacion = ?, funcionObjetivo = ? WHERE problemaID = ?",
         problemaPL
    )
    await db.commit()
    
async def eliminar_problema(db: aiosqlite.Connection, problema_id: str):
    if not await existe_problema(db, problema_id):
        return False
        
    await db.execute(
        "DELETE FROM problemaPL WHERE problemaID = ?",
        (problema_id,)
    )
    await db.commit()
        
    return True