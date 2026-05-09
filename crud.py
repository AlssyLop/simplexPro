import aiosqlite
from schemas import ProblemaPLCreate
import uuid

async def create_problema(db: aiosqlite.Connection, p: ProblemaPLCreate):
    # 1. Insertar Problema
    problema_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO problemaPL (problemaID, titulo, descripcion, tipoOptimizacion, funcionObjetivo) VALUES (?, ?, ?, ?, ?)",
        (problema_id, p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), f"{p.funcion_objetivo.x}x + {p.funcion_objetivo.y}y")
    )

    # 2. Insertar Variables
    for var_key, var_nombre in p.variables.items():
        var_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO variables (variableID, variable, nombre, problemaID) VALUES (?, ?, ?, ?)",
            (var_id, var_key, var_nombre, problema_id)
        )

    # 3. Insertar Restricciones y Términos
    for restr in p.restricciones:
        restr_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO restricciones (restriccionID, problemaID, constante, operador, glosa) VALUES (?, ?, ?, ?, ?)",
            (restr_id, problema_id, restr.valor, restr.signo, restr.glosa)
        )
        
        # Obtener IDs de variables para los términos
        # (Esto es un poco ineficiente, en un sistema real se haría mejor)
        for var_key in ["x", "y"]:
            cursor = await db.execute("SELECT variableID FROM variables WHERE problemaID = ? AND variable = ?", (problema_id, var_key))
            row = await cursor.fetchone()
            if row:
                var_id = row[0]
                coef = restr.x if var_key == "x" else restr.y
                await db.execute(
                    "INSERT INTO terminos (terminoID, restriccionID, variableID, coeficiente) VALUES (?, ?, ?, ?)",
                    (str(uuid.uuid4()), restr_id, var_id, coef)
                )

    await db.commit()
    return problema_id

async def get_problemas(db: aiosqlite.Connection):
    cursor = await db.execute("SELECT problemaID, titulo, fechaCreacion FROM problemaPL ORDER BY fechaCreacion DESC")
    rows = await cursor.fetchall()
    return [{"id": r[0], "titulo": r[1], "fecha_creacion": r[2]} for r in rows]

async def delete_problema(db: aiosqlite.Connection, problema_id: str):
    await db.execute("DELETE FROM problemaPL WHERE problemaID = ?", (problema_id,))
    await db.commit()

async def update_problema(db: aiosqlite.Connection, problema_id: str, p: ProblemaPLCreate):
    # Borrar viejos y poner nuevos (más simple para SQLite con cascada)
    # Primero verificamos que existe
    cursor = await db.execute("SELECT 1 FROM problemaPL WHERE problemaID = ?", (problema_id,))
    if not await cursor.fetchone():
        return False
    
    # Borrar dependencias (aunque ON DELETE CASCADE debería ayudar si borramos el padre)
    # Pero queremos mantener el mismo ID de problema, así que borramos hijos y actualizamos padre.
    await db.execute("DELETE FROM variables WHERE problemaID = ?", (problema_id,))
    await db.execute("DELETE FROM restricciones WHERE problemaID = ?", (problema_id,))
    
    # Actualizar Padre
    await db.execute(
        "UPDATE problemaPL SET titulo = ?, descripcion = ?, tipoOptimizacion = ?, funcionObjetivo = ? WHERE problemaID = ?",
        (p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), f"{p.funcion_objetivo.x}x + {p.funcion_objetivo.y}y", problema_id)
    )

    # Re-insertar Variables y Restricciones (usando la lógica de create pero con ID fijo)
    for var_key, var_nombre in p.variables.items():
        var_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO variables (variableID, variable, nombre, problemaID) VALUES (?, ?, ?, ?)",
            (var_id, var_key, var_nombre, problema_id)
        )

    for restr in p.restricciones:
        restr_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO restricciones (restriccionID, problemaID, constante, operador, glosa) VALUES (?, ?, ?, ?, ?)",
            (restr_id, problema_id, restr.valor, restr.signo, restr.glosa)
        )
        for var_key in ["x", "y"]:
            cursor = await db.execute("SELECT variableID FROM variables WHERE problemaID = ? AND variable = ?", (problema_id, var_key))
            row = await cursor.fetchone()
            if row:
                var_id = row[0]
                coef = restr.x if var_key == "x" else restr.y
                await db.execute(
                    "INSERT INTO terminos (terminoID, restriccionID, variableID, coeficiente) VALUES (?, ?, ?, ?)",
                    (str(uuid.uuid4()), restr_id, var_id, coef)
                )

    await db.commit()
    return True
