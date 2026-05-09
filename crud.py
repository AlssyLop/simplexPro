import aiosqlite
from schemas import ProblemaPLCreate
import uuid
import json
import re

async def create_problema(db: aiosqlite.Connection, p: ProblemaPLCreate):
    # 1. Insertar Problema y obtener ID generado usando RETURNING
    cursor = await db.execute(
        "INSERT INTO problemaPL (titulo, descripcion, tipoOptimizacion, funcionObjetivo) VALUES (?, ?, ?, ?) RETURNING problemaID",
        (p.titulo, p.descripcion, p.funcion_objetivo.tipo.upper(), f"{p.funcion_objetivo.x}x + {p.funcion_objetivo.y}y")
    )
    row = await cursor.fetchone()
    problema_id = row[0]

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

async def get_problema_completo(db: aiosqlite.Connection, problema_id: str) -> dict | None:
    """
    Obtiene toda la estructura de un problema en una sola consulta usando magia JSON de SQLite.
    """
    query = """
    SELECT 
        p.titulo, 
        p.descripcion, 
        p.tipoOptimizacion, 
        p.funcionObjetivo,
        (SELECT json_group_object(variable, nombre) FROM variables WHERE problemaID = p.problemaID) as variables_json,
        (SELECT json_group_array(
            json_object(
                'signo', r.operador,
                'valor', r.constante,
                'glosa', r.glosa,
                'x', (SELECT t.coeficiente FROM terminos t JOIN variables v ON t.variableID = v.variableID WHERE t.restriccionID = r.restriccionID AND v.variable = 'x'),
                'y', (SELECT t.coeficiente FROM terminos t JOIN variables v ON t.variableID = v.variableID WHERE t.restriccionID = r.restriccionID AND v.variable = 'y')
            )
        ) FROM restricciones r WHERE r.problemaID = p.problemaID) as restricciones_json
    FROM problemaPL p
    WHERE p.problemaID = ?
    """
    # Nota: Si el problema tiene más de 2 variables, la consulta JSON se puede generalizar más,
    # pero para el Método Gráfico (que es el que exporta a PDF), 'x' e 'y' son fijos.

    cursor = await db.execute(query, (problema_id,))
    row = await cursor.fetchone()
    if not row:
        return None

    # Parsear JSONs devueltos por SQLite
    variables = json.loads(row["variables_json"])
    restricciones = json.loads(row["restricciones_json"])

    # Limpiar restricciones (quitar None de x/y si no existen)
    for r in restricciones:
        if r['x'] is None: r['x'] = 0.0
        if r['y'] is None: r['y'] = 0.0

    # Extraer coeficientes de FO desde el string (Mejorado)
    fo_str = row["funcionObjetivo"].replace(" ", "")
    # Intentamos buscar coeficientes basándonos en los nombres de variables encontrados
    x_val, y_val = 0.0, 0.0
    try:
        x_match = re.search(r'([\d\.\-]+)x', fo_str)
        y_match = re.search(r'([\d\.\-]+)y', fo_str)
        x_val = float(x_match.group(1)) if x_match else 0.0
        y_val = float(y_match.group(1)) if y_match else 0.0
    except: pass

    return {
        "titulo": row["titulo"],
        "descripcion": row["descripcion"],
        "variables": variables,
        "restricciones": restricciones,
        "funcion_objetivo": {
            "x": x_val,
            "y": y_val,
            "tipo": row["tipoOptimizacion"].lower()
        }
    }

import base64

async def save_resultado_grafico(db: aiosqlite.Connection, problema_id: str, resultado: dict):
    # Decodificar base64 a bytes
    grafico_bytes = None
    if "img" in resultado:
        try:
            # Eliminar prefijo si lo tiene ("data:image/png;base64,")
            b64_str = resultado["img"]
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            grafico_bytes = base64.b64decode(b64_str)
        except Exception:
            pass

    valores_fo_json = json.dumps(resultado.get("valores_fo", []))
    mensaje = resultado.get("mensaje", "")

    # Borrar si ya existe un resultado anterior para este problema
    await db.execute("DELETE FROM metodoGrafico WHERE problemaID = ?", (problema_id,))
    
    await db.execute(
        "INSERT INTO metodoGrafico (problemaID, valoresFO, mensaje, grafico) VALUES (?, ?, ?, ?)",
        (problema_id, valores_fo_json, mensaje, grafico_bytes)
    )
    await db.commit()

async def save_resultado_simplex(db: aiosqlite.Connection, problema_id: str, resultado: dict):
    iteraciones_json = json.dumps(resultado.get("iteraciones", []))
    valor_fo_json = json.dumps(resultado.get("valor_fo", ""))
    mensaje = resultado.get("mensaje", "")

    # Borrar si ya existe un resultado anterior para este problema
    await db.execute("DELETE FROM metodoSimple WHERE problemaID = ?", (problema_id,))
    
    await db.execute(
        "INSERT INTO metodoSimple (problemaID, iteraciones, valorFo, mensaje) VALUES (?, ?, ?, ?)",
        (problema_id, iteraciones_json, valor_fo_json, mensaje)
    )
    await db.commit()
