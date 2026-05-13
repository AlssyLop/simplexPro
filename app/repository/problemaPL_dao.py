import aiosqlite
from app.schemas.problemaPL_model import ResumenProblema, ProblemaPL

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

async def registrar_variables(db, variables):
    await db.executemany(
        "INSERT INTO variables (variable, nombre, problemaID) VALUES (?, ?, ?)",
        variables
    )
    await db.commit()

async def registrar_restricciones(db, restricciones):
    await db.executemany(
        "INSERT INTO restricciones (problemaID, inecuacion, glosa) VALUES (?, ?, ?)",
        restricciones
    )
    await db.commit()

async def listar_problemas(db: aiosqlite.Connection, offset: int):
    cursor = await db.execute(
        "SELECT problemaID, tipoOptimizacion, titulo, descripcion, fechaCreacion FROM problemaPL LIMIT 10 OFFSET ?",
        (offset,)
    )
    lista_problemasPL = await cursor.fetchall()
    lista_problemasPL = [ResumenProblema(
            id = row[0],
            tipoOptimizacion = row[1],
            titulo = row[2],
            descripcion = row[3],
            fechaCreacion = row[4]
        ) for row in lista_problemasPL]

    return lista_problemasPL

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