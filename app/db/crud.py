import aiosqlite
from app.schemas.problema import ProblemaPLCreate
import uuid
import json
import re

    

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