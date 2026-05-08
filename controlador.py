from fastapi import HTTPException

SIGNOS_GRAFICO = {"<=", ">="}
SIGNOS_SIMPLEX = {"<=", ">=", "="}
TIPOS_OPT = {"max", "min"}


def _es_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ---------------------------------------------------------------------------
# Validaciones: Método Gráfico
# ---------------------------------------------------------------------------

def validar_grafico(problemaPL: dict):
    """
    Valida la estructura del problema antes de enviarlo a metodoGrafico.
    Lanza HTTPException 422 si encuentra errores.
    """
    errores = []

    # 1. Claves raíz obligatorias
    for clave in ("variables", "restricciones", "funcion_objetivo"):
        if clave not in problemaPL:
            errores.append(f"Falta la clave obligatoria: '{clave}'.")

    if errores:
        raise HTTPException(status_code=422, detail=errores)

    variables = problemaPL["variables"]
    restricciones = problemaPL["restricciones"]
    fo = problemaPL["funcion_objetivo"]

    # 2. Variables: debe contener exactamente 'x' e 'y'
    if not isinstance(variables, dict):
        errores.append("'variables' debe ser un objeto/diccionario.")
    else:
        for var in ("x", "y"):
            if var not in variables:
                errores.append(f"'variables' debe contener la clave '{var}'.")
            elif not isinstance(variables[var], str) or not variables[var].strip():
                errores.append(f"El nombre de la variable '{var}' debe ser una cadena no vacía.")

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        errores.append("'restricciones' debe ser una lista con al menos un elemento.")
    else:
        for idx, r in enumerate(restricciones):
            prefijo = f"Restricción [{idx}]"
            if not isinstance(r, dict):
                errores.append(f"{prefijo}: debe ser un objeto.")
                continue
            for var in ("x", "y"):
                if var not in r:
                    errores.append(f"{prefijo}: falta el coeficiente '{var}'.")
                elif not _es_numero(r[var]):
                    errores.append(f"{prefijo}: el coeficiente '{var}' debe ser numérico.")
            if "signo" not in r:
                errores.append(f"{prefijo}: falta 'signo'.")
            elif r["signo"] not in SIGNOS_GRAFICO:
                errores.append(f"{prefijo}: 'signo' debe ser uno de {SIGNOS_GRAFICO}.")
            if "valor" not in r:
                errores.append(f"{prefijo}: falta 'valor'.")
            elif not _es_numero(r["valor"]):
                errores.append(f"{prefijo}: 'valor' debe ser numérico.")

    # 4. Función objetivo
    if not isinstance(fo, dict):
        errores.append("'funcion_objetivo' debe ser un objeto/diccionario.")
    else:
        for var in ("x", "y"):
            if var not in fo:
                errores.append(f"'funcion_objetivo' falta el coeficiente '{var}'.")
            elif not _es_numero(fo[var]):
                errores.append(f"'funcion_objetivo.{var}' debe ser numérico.")
        if "tipo" not in fo:
            errores.append("'funcion_objetivo' falta 'tipo'.")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            errores.append(f"'funcion_objetivo.tipo' debe ser 'max' o 'min', recibido: '{fo['tipo']}'.")

    if errores:
        raise HTTPException(status_code=422, detail=errores)


# ---------------------------------------------------------------------------
# Validaciones: Método Simplex
# ---------------------------------------------------------------------------

def validar_simplex(problemaPL: dict):
    """
    Valida la estructura del problema antes de enviarlo a metodoSimplex.
    Lanza HTTPException 422 si encuentra errores.
    """
    errores = []

    # 1. Claves raíz obligatorias
    for clave in ("variables", "restricciones", "funcion_objetivo"):
        if clave not in problemaPL:
            errores.append(f"Falta la clave obligatoria: '{clave}'.")

    if errores:
        raise HTTPException(status_code=422, detail=errores)

    variables = problemaPL["variables"]
    restricciones = problemaPL["restricciones"]
    fo = problemaPL["funcion_objetivo"]

    # 2. Variables: dict con al menos 1 variable, nombres tipo string
    if not isinstance(variables, dict) or len(variables) == 0:
        errores.append("'variables' no es valido")
    else:
        for var, nombre in variables.items():
            if not isinstance(nombre, str) or not nombre.strip():
                errores.append(f"El nombre de la variable '{var}' no es valido")

    vars_keys = list(variables.keys()) if isinstance(variables, dict) else []

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        errores.append("'restricciones' no es valido")
    else:
        for idx, r in enumerate(restricciones):
            prefijo = f"Restricción [{idx}]"
            if not isinstance(r, dict):
                errores.append(f"{prefijo}: debe ser un objeto")
                continue
            # Coeficientes de variables
            for var in vars_keys:
                if var in r and not _es_numero(r[var]):
                    errores.append(f"{prefijo}: el coeficiente '{var}' no es valido")
            # signo
            if "signo" not in r:
                errores.append(f"{prefijo}: falta el signo")
            elif r["signo"] not in SIGNOS_SIMPLEX:
                errores.append(f"{prefijo}: el signo no es valido")
            # valor
            if "valor" not in r:
                errores.append(f"{prefijo}: falta el valor")
            elif not _es_numero(r["valor"]):
                errores.append(f"{prefijo}: el valor no es valido")

    # 4. Función objetivo
    if not isinstance(fo, dict):
        errores.append("'funcion_objetivo' no es valido")
    else:
        for var in vars_keys:
            if var in fo and not _es_numero(fo[var]):
                errores.append(f"'funcion_objetivo.{var}' no es valido")
        if "tipo" not in fo:
            errores.append("'funcion_objetivo' falta el tipo")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            errores.append(f"'funcion_objetivo' el tipo no es valido")

    if errores:
        raise HTTPException(status_code=422, detail=errores)