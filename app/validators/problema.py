from fastapi import HTTPException
import re
# from app.schemas.grafico_model import ProblemaPL as ProblemaGrafico
# from app.schemas.simplex_model import ProblemaPL as ProblemaSimplex

SIGNOS_GRAFICO = {"=", "<=", ">="}
SIGNOS_SIMPLEX = {"<=", ">=", "="}
TIPOS_OPT = {"max", "min"}


def _es_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ---------------------------------------------------------------------------
# Validaciones: Método Gráfico
# ---------------------------------------------------------------------------

def validar_problema_grafico(problema: dict):
    """
    Valida la estructura del problema antes de enviarlo a metodoGrafico.
    Lanza HTTPException 422 si encuentra errores.
    """
    # 1. Claves raíz obligatorias
    for clave in ("titulo", "descripcion", "variables", "restricciones", "funcion_objetivo"):
        if clave not in problema:
            raise HTTPException(status_code=400, detail=f"{clave} es requerido")

    variables = problema["variables"]
    restricciones = problema["restricciones"]
    fo = problema["funcion_objetivo"]

    # 2. Variables: debe contener exactamente 'x' e 'y'
    if not isinstance(variables, dict):
        raise HTTPException(status_code=400, detail="variables es requerido")
    else:
        for var in ("x", "y"):
            if var not in variables:
                raise HTTPException(status_code=400, detail=f"La variable '{var}' es requerida")
            elif not isinstance(variables[var], str) or not variables[var].strip():
                raise HTTPException(status_code=400, detail=f"El nombre de la variable '{var}' es requerido")

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        raise HTTPException(status_code=400, detail="restricciones es requerido")
    else:
        for idx, r in enumerate(restricciones):
            prefijo = f"la restricción ({idx + 1})"
            if not isinstance(r, dict):
                raise HTTPException(status_code=400, detail=f"{prefijo}: no es valido")
            for var in ("x", "y"):
                if var not in r:
                    raise HTTPException(status_code=400, detail=f"{prefijo}: falta coeficiente '{var}'")
                elif not _es_numero(r[var]):
                    raise HTTPException(status_code=400, detail=f"{prefijo}: coeficiente '{var}' no es valido")
            if "signo" not in r:
                raise HTTPException(status_code=400, detail=f"{prefijo}: falta signo")
            elif r["signo"] not in SIGNOS_GRAFICO:
                raise HTTPException(status_code=400, detail=f"El signo de {prefijo} no es valido")
            if "valor" not in r:
                raise HTTPException(status_code=400, detail=f"{prefijo}: falta 'valor'")
            elif not _es_numero(r["valor"]):
                raise HTTPException(status_code=400, detail=f"{prefijo}: valor no es valido")

    # 4. Función objetivo
    if not isinstance(fo, dict):
        raise HTTPException(status_code=400, detail="función objetivo requerido")
    else:
        for var in ("x", "y"):
            if var not in fo:
                raise HTTPException(status_code=400, detail=f"Coeficiente '{var}' en función objetivo requerido")
            elif not _es_numero(fo[var]):
                raise HTTPException(status_code=400, detail=f"Coeficiente '{var}' en función objetivo debe ser numérico")
        if "tipo" not in fo:
            raise HTTPException(status_code=400, detail="Tipo de optimización requerido")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            raise HTTPException(status_code=400, detail=f"Tipo de optimización inválido: '{fo['tipo']}'")


# ---------------------------------------------------------------------------
# Validaciones: Método Simplex
# ---------------------------------------------------------------------------

def validar_problema_simplex(problema: dict):
    """
    Valida la estructura del problema antes de enviarlo a metodoSimplex.
    Lanza HTTPException 422 si encuentra errores.
    """
    # 1. Claves raíz obligatorias
    for clave in ("variables", "restricciones", "funcion_objetivo"):
        if clave not in problema:
            raise HTTPException(status_code=400, detail=f"{clave} es requerido")

    variables = problema["variables"]
    restricciones = problema["restricciones"]
    fo = problema["funcion_objetivo"]

    # 2. Variables: dict con al menos 1 variable, nombres tipo string
    if not isinstance(variables, dict) or len(variables) == 0:
        raise HTTPException(status_code=400, detail="'Las variables' no son validas.")
    else:
        #validar si var tiene el formato x1, x2, x3...xn
        for var, nombre in variables.items():
            if not re.match(r'^x\d+$', var):
                raise HTTPException(status_code=400, detail=f"Variable '{var}' no es valida.")
            if not isinstance(nombre, str) or not nombre.strip():
                raise HTTPException(status_code=400, detail=f"Nombre variable '{var}' inválido.")

    # 3. Restricciones: lista no vacía
    if not isinstance(restricciones, list) or len(restricciones) == 0:
        raise HTTPException(status_code=400, detail="'restricciones' no son validas.")
    else:
        for idx, r in enumerate(restricciones):
            if not isinstance(r, dict):
                raise HTTPException(status_code=400, detail="Restricción inválida.")
            # validar coeficientes con el fromato x1, x2, x3...xn
            for var in variables.keys():
                if var not in r:
                    raise HTTPException(status_code=400, detail=f"Restricción {idx}: falta coeficiente '{var}'")
                elif not _es_numero(r[var]):
                    raise HTTPException(status_code=400, detail=f"Restricción {idx}: el coeficiente '{var}' no es valido")
            # validar signo
            if "signo" not in r:
                raise HTTPException(status_code=400, detail=f"Restricción {idx}: falta signo.")
            elif r["signo"] not in SIGNOS_SIMPLEX:
                raise HTTPException(status_code=400, detail=f"Restricción {idx}: signo inválido. Use <=, >= o =.")
            # validar constante
            if "valor" not in r:
                raise HTTPException(status_code=400, detail=f"Restricción {idx}: falta valor constante.")
            elif not _es_numero(r["valor"]):
                raise HTTPException(status_code=400, detail=f"Restricción {idx}: valor constante debe ser numérico.")
            
    # 4. Función objetivo
    if not isinstance(fo, dict):
        raise HTTPException(status_code=400, detail="'función objetivo' no es valida")
    else:
        # validar que las variables de la FO sean validas:
        for var in variables.keys():
            if var not in fo:
                raise HTTPException(status_code=400, detail=f"El coeficiente '{var}' no es valido")
            elif not _es_numero(fo[var]):
                raise HTTPException(status_code=400, detail=f"El coeficiente '{var}' no es valido")
        # validar tipo
        if "tipo" not in fo:
            raise HTTPException(status_code=400, detail="Tipo de optimización faltante en FO.")
        elif fo["tipo"].lower() not in TIPOS_OPT:
            raise HTTPException(status_code=400, detail=f"Tipo '{fo['tipo']}' inválido. Use 'max' o 'min'.")