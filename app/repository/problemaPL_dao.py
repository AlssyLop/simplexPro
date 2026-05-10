
async def registrar_problemaPL(db, problemaPL):
    cursor = await db.execute(
        "INSERT INTO problemaPL (titulo, descripcion, tipoOptimizacion, funcionObjetivo) VALUES (?, ?, ?, ?) RETURNING problemaID",
        problemaPL
    )
    return await cursor.fetchone()[0]

async def registrar_variables(db, variables):
    await db.executemany(
        "INSERT INTO variables (variable, nombre, problemaID) VALUES (?, ?, ?)",
        variables
    )

async def registrar_restricciones(db, restricciones):
    await db.executemany(
        "INSERT INTO restricciones (problemaID, inecuacion, glosa) VALUES (?, ?, ?)",
        restricciones
    )