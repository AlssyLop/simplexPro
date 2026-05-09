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
        errores.append("variable requerido.")
    else:
        for var in ("x", "y"):
            if var not in variables:
                errores.append(f"Variable '{var}' faltante.")
            elif not isinstance(variables[var], str) or not variables[var].strip():
                errores.append(f"El nombre de la variable '{var}' es requerido.")

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        errores.append("restricciones es requerido.")
    else:
        for idx, r in enumerate(restricciones):
            prefijo = f"Restricción [{idx}]"
            if not isinstance(r, dict):
                errores.append(f"{prefijo}: debe ser un objeto.")
                continue
            for var in ("x", "y"):
                if var not in r:
                    errores.append(f"{prefijo}: falta coeficiente '{var}'.")
                elif not _es_numero(r[var]):
                    errores.append(f"{prefijo}: coeficiente '{var}' debe ser numérico.")
            if "signo" not in r:
                errores.append(f"{prefijo}: falta 'signo'.")
            elif r["signo"] not in SIGNOS_GRAFICO:
                errores.append(f"{prefijo}: signo inválido. Use <= o >=.")
            if "valor" not in r:
                errores.append(f"{prefijo}: falta 'valor' (constante).")
            elif not _es_numero(r["valor"]):
                errores.append(f"{prefijo}: valor constante debe ser numérico.")

    # 4. Función objetivo
    if not isinstance(fo, dict):
        errores.append("función objetivo requerida.")
    else:
        for var in ("x", "y"):
            if var not in fo:
                errores.append(f"Coeficiente '{var}' faltante en función objetivo.")
            elif not _es_numero(fo[var]):
                errores.append(f"Coeficiente '{var}' en función objetivo debe ser numérico.")
        if "tipo" not in fo:
            errores.append("Tipo de optimización ('max'/'min') faltante.")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            errores.append(f"Tipo de optimización inválido: '{fo['tipo']}'. Use 'max' o 'min'.")

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
        errores.append("'Las variables' no son validas.")
    else:
        for var, nombre in variables.items():
            if not isinstance(nombre, str) or not nombre.strip():
                errores.append(f"Nombre para variable '{var}' inválido.")

    vars_keys = list(variables.keys()) if isinstance(variables, dict) else []

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        errores.append("'restricciones' no son validas.")
    else:
        for idx, r in enumerate(restricciones):
            if not isinstance(r, dict):
                errores.append("Restricción inválida.")
                continue
            # Coeficientes de variables
            for var in vars_keys:
                if var in r and not _es_numero(r[var]):
                    errores.append(f"Restricción {idx}: el coeficiente '{var}' no es valido")
            # signo
            if "signo" not in r:
                errores.append(f"Restricción {idx}: falta signo.")
            elif r["signo"] not in SIGNOS_SIMPLEX:
                errores.append(f"Restricción {idx}: signo inválido. Use <=, >= o =.")
            # valor
            if "valor" not in r:
                errores.append(f"Restricción {idx}: falta valor constante.")
            elif not _es_numero(r["valor"]):
                errores.append(f"{prefijo}: valor constante debe ser numérico.")

    # 4. Función objetivo
    if not isinstance(fo, dict):
        errores.append("'función objetivo' no es valida")
    else:
        for var in vars_keys:
            if var in fo and not _es_numero(fo[var]):
                errores.append(f"El coeficiente '{var}' no es valido")
        if "tipo" not in fo:
            errores.append("Tipo de optimización faltante en FO.")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            errores.append(f"Tipo '{fo['tipo']}' inválido. Use 'max' o 'min'.")

    if errores:
        raise HTTPException(status_code=422, detail=errores)