import numpy as np
from app.schemas.problemaPL import ProblemaPL
from app.schemas.resultados import Iteracion, ResultadoSimplex

def metodoSimplex(problemaPL:ProblemaPL):
    """
    Método iterativo para resolver modelos de programación lineal (Simplex / Dos Fases o Gran M).
    Se usa Pandas para mostrar la tabla iterativa con formato ASCII.
    """
    vars_nombres = problemaPL.variables
    restricciones = problemaPL.restricciones
    fo = problemaPL.funcion_objetivo
    tipo_opt = fo.tipo.lower()

    vars_keys = list(vars_nombres.keys())
    num_vars = len(vars_keys)
    num_res = len(restricciones)

    holguras = []
    artificiales = []
    M = 1e7  # Gran M para penalizar artificiales

    for i, r in enumerate(restricciones):
        signo = r.signo
        if signo == "<=":
            holguras.append(f"S{i+1}")
        elif signo == ">=":
            holguras.append(f"S{i+1}")
            artificiales.append(f"A{i+1}")
        elif signo == "=":
            artificiales.append(f"A{i+1}")

    cols = vars_keys + holguras + artificiales + ["R"]
    num_cols = len(cols)

    tabla = np.zeros((num_res + 1, num_cols))
    z_row = num_res

    # Fila Z inicial
    for j, vk in enumerate(vars_keys):
        val = fo.variables.terminos[j].coeficiente
        tabla[z_row, j] = -val if tipo_opt == "max" else val

    base = []
    cb = []

    h_idx = 0
    a_idx = 0
    for i, r in enumerate(restricciones):
        for j, vk in enumerate(vars_keys):
            tabla[i, j] = r.variables.terminos[j].coeficiente

        tabla[i, -1] = r.constante

        signo = r.signo
        if signo == "<=":
            tabla[i, num_vars + h_idx] = 1
            base.append(holguras[h_idx])
            cb.append(0)
            h_idx += 1
        elif signo == ">=":
            tabla[i, num_vars + h_idx] = -1
            a_col = num_vars + len(holguras) + a_idx
            tabla[i, a_col] = 1
            base.append(artificiales[a_idx])
            if tipo_opt == "max":
                cb.append(-M)
                tabla[z_row, a_col] = M
                tabla[z_row, :] -= M * tabla[i, :]
            else:
                cb.append(M)
                tabla[z_row, a_col] = -M
                tabla[z_row, :] += M * tabla[i, :]
            h_idx += 1
            a_idx += 1
        elif signo == "=":
            a_col = num_vars + len(holguras) + a_idx
            tabla[i, a_col] = 1
            base.append(artificiales[a_idx])
            if tipo_opt == "max":
                cb.append(-M)
                tabla[z_row, a_col] = M
                tabla[z_row, :] -= M * tabla[i, :]
            else:
                cb.append(M)
                tabla[z_row, a_col] = -M
                tabla[z_row, :] += M * tabla[i, :]
            a_idx += 1

    # --- Helpers ---
    def fmt(v):
        """Entero si no tiene decimales, float redondeado a 2 si los tiene."""
        if isinstance(v, float) and abs(v) < 1e-8:
            return 0
        rounded = round(float(v), 2)
        return int(rounded) if rounded == int(rounded) else rounded

    def tabla_a_dict(tabla_np, base_actual, cb_actual):
        """Convierte todas las filas (restricciones + fila Z) a dict columna→lista."""
        data = {}
        # cb: valores de restricciones + "" para la fila Z
        data["cb"] = [fmt(c) if abs(c) < M else ("-M" if c < 0 else "M") for c in cb_actual] + [""]
        data["base"] = list(base_actual) + ["Z"]
        for col_name, col_idx in zip(cols[:-1], range(len(cols) - 1)):  # sin "R"
            data[col_name] = [fmt(tabla_np[row, col_idx]) for row in range(num_res + 1)]
        data["R"] = [fmt(tabla_np[row, -1]) for row in range(num_res + 1)]
        return data

    

    tabla_ant = tabla_a_dict(tabla, list(base), list(cb))
    iteraciones = []

    def guardar_iteracion(entra,sale,pivote,razon_minima):
        iteracion = Iteracion(
            iteracion=len(iteraciones) + 1,
            entra=entra,
            sale=sale,
            razonMinima=razon_minima,
            elementoPivote=pivote,
            tabla=tabla_ant,
        )
        iteraciones.append(iteracion)

    while True:
        z_vals = tabla[z_row, :-1]

        if tipo_opt == "max":
            if np.all(z_vals >= -1e-8):
                guardar_iteracion("","","","")    
                break
            col_pivote = int(np.argmin(z_vals))
        else:
            if np.all(z_vals <= 1e-8):
                guardar_iteracion("","","","") 
                break
            col_pivote = int(np.argmax(z_vals))

        col_vals = tabla[:-1, col_pivote]
        rhs = tabla[:-1, -1]
        ratios = np.full(num_res, np.inf)

        for i in range(num_res):
            if col_vals[i] > 1e-8:
                ratios[i] = rhs[i] / col_vals[i]

        if np.all(ratios == np.inf):
            return {"Error": "El problema no tiene solución (es no acotado)."}

        fila_pivote = int(np.argmin(ratios))
        pivote = tabla[fila_pivote, col_pivote]
        razon_minima = ratios[fila_pivote]

        entra = cols[col_pivote]
        sale = base[fila_pivote]

        # Operaciones Gauss-Jordan
        tabla[fila_pivote, :] /= pivote
        for i in range(num_res + 1):
            if i != fila_pivote:
                tabla[i, :] -= tabla[i, col_pivote] * tabla[fila_pivote, :]

        base[fila_pivote] = entra
        if entra in vars_keys:
            cb[fila_pivote] = fo.get(entra, 0) if tipo_opt == "max" else -fo.get(entra, 0)
        elif entra in holguras:
            cb[fila_pivote] = 0
        elif entra in artificiales:
            cb[fila_pivote] = -M if tipo_opt == "max" else M

        guardar_iteracion(entra,sale,fmt(pivote),fmt(razon_minima))
        tabla_ant = tabla_a_dict(tabla, list(base), list(cb))
    
    
    # --- Resultados finales ---
    z_val = tabla[z_row, -1]
    if tipo_opt == "min":
        z_val = -z_val

    vars_optimas = ""
    valorFo = f"Z = "
    for vk in vars_keys:
        val = tabla[base.index(vk), -1] if vk in base else 0
        valorFo += f"{fmt(val)}{vk} + "
        if fmt(val) != 0:
            vars_optimas += f"{fmt(val):,} {vars_nombres[vk]}, "
    valor_fo = f"{valorFo.strip().rstrip('+').strip()} = {fmt(z_val):,}"
    vars_optimas = vars_optimas.strip().rstrip(',').strip()
    #Crear mensaje general para cualquier problema: 
    tipo_texto = "máximo" if tipo_opt == "max" else "mínimo"
    if vars_optimas == "":
        mensaje = (
            f"El valor óptimo de {tipo_texto} es {fmt(z_val):,}"
        )
    else:
        mensaje = (
            f"La solución óptima es {vars_optimas} con un valor {tipo_texto} de Z = {fmt(z_val):,}"
        )
    funcion_objetivo = f"{tipo_opt.upper()} Z = "
    for key, value in fo.items():
        if key != "tipo":
            funcion_objetivo += f"{value}{key} + "
    funcion_objetivo = funcion_objetivo.strip().rstrip('+').strip()

    resultado = ResultadoSimplex(
        iteraciones=iteraciones,
        valorFO=valor_fo,
        mensaje=mensaje,
        funcion_objetivo=funcion_objetivo
    )
    return resultado
