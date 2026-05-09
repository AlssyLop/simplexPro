import io
import numpy as np
import matplotlib.pyplot as plt
import base64

def metodoGrafico(problemaPL):
    """
    Metodo grafico para resolver problemas de Programación Lineal de 2 variables.
    """
    vars_nombres = problemaPL["variables"]
    restricciones = problemaPL["restricciones"]
    fo = problemaPL["funcion_objetivo"]
    tipo_opt = fo["tipo"].lower()

    def interseccion(r1, r2):
        """Resuelve el sistema de ecuaciones entre dos rectas."""
        a = np.array([[r1['x'], r1['y']], [r2['x'], r2['y']]])
        b = np.array([r1['valor'], r2['valor']])
        try:
            return np.linalg.solve(a, b)
        except np.linalg.LinAlgError:
            return None

    def es_factible(p, lista):
        x, y = p 
        margen = 1e-8
        for r in lista:
            val = r['x']*x + r['y']*y
            if r['signo'] == "<=" and val > r['valor'] + margen: return False
            if r['signo'] == ">=" and val < r['valor'] - margen: return False
        return True

    # --- PASO 2: Hallar Vértices de la Región Factible ---
    puntos_v = []
    n = len(restricciones)
    for i in range(n):
        for j in range(i+1, n):
            p = interseccion(restricciones[i], restricciones[j])
            if p is not None and es_factible(p, restricciones):
                if not any(np.allclose(p, v) for v in puntos_v):
                    puntos_v.append(p)

    if not puntos_v:
        return {"Error": "No se encontró una región factible."}

    # --- PASO 3: Evaluación de la Función Objetivo ---
    resultados = []
    for v in puntos_v:
        # Validar si (v[0]->x,v[1]->y) son enteros y redondear si no lo son
        if v[0] % 1 != 0:
            v[0] = round(v[0])
        if v[1] % 1 != 0:
            v[1] = round(v[1])
        z = fo['x']*v[0] + fo['y']*v[1]
        resultados.append({'p': v, 'z': z})

    # Buscar el óptimo según sea MAX o MIN
    if tipo_opt == "max":
        optimo = max(resultados, key=lambda x: x['z'])
    else:
        optimo = min(resultados, key=lambda x: x['z'])

    # --- PASO 4: Visualización Gráfica ---
    plt.figure(figsize=(11, 7))
    ax = plt.gca()
    
    # Límites dinámicos
    max_x = max([v[0] for v in puntos_v] + [5]) + 2
    max_y = max([v[1] for v in puntos_v] + [5]) + 2
    x_rango = np.linspace(0, max_x, 500)

    # Dibujar líneas de restricciones
    for i, res in enumerate(restricciones):
        etiqueta = f"R{i+1}: {res['x']}x + {res['y']}y {res['signo']} {res['valor']}"
        if res['y'] != 0:
            y_r = (res['valor'] - res['x']*x_rango) / res['y']
            plt.plot(x_rango, y_r, label=etiqueta, linewidth=2)
        else:
            plt.axvline(res['valor']/res['x'], label=etiqueta, linewidth=2)

    # Dibujar Región Factible (Polígono)
    if len(puntos_v) >= 3:
        # Ordenar vértices para el polígono
        centro = np.mean(puntos_v, axis=0)
        puntos_v_ord = sorted(puntos_v, key=lambda p: np.arctan2(p[1]-centro[1], p[0]-centro[0]))
        poligono = plt.Polygon(puntos_v_ord, color='green', alpha=0.15, label='Región Factible')
        ax.add_patch(poligono)

    # Dibujar vértices y etiquetas
    for res_v in resultados:
        v = res_v['p']
        plt.plot(v[0], v[1], 'ko', markersize=4, zorder=4)
        offset = 0.3
        plt.text(v[0]+offset, v[1]+offset, f"({v[0]:.1f}, {v[1]:.1f})\nZ={res_v['z']:.2f}", 
                 fontsize=8, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # MARCAR EL ÓPTIMO CON ESTRELLA
    plt.scatter(optimo['p'][0], optimo['p'][1], color='red', marker='*', s=300, 
                edgecolor='black', label=f'SOLUCIÓN ÓPTIMA (Z={optimo["z"]:.2f})', zorder=10)

    # Configuración de ejes
    plt.axhline(0, color='black', linewidth=1.5, zorder=3)
    plt.axvline(0, color='black', linewidth=1.5, zorder=3)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(-0.5, max_x)
    plt.ylim(-0.5, max_y)
    plt.xlabel(vars_nombres['x'])
    plt.ylabel(vars_nombres['y'])
    plt.title(f"Método Gráfico - Optimización {tipo_opt.upper()} Z = {fo['x']}x + {fo['y']}y", fontsize=14)
    plt.legend(loc='upper right', fontsize=9)

    # Guardar resultados
    resultado = {"valores_fo":[]}
    resultado['funcion_objetivo'] = f"{fo['x']}x + {fo['y']}y"
    for i, rv in enumerate(resultados):
        resultado['valores_fo'].append(f"f({rv['p'][0]}, {rv['p'][1]}) = {fo['x']}*({rv['p'][0]}) + {fo['y']}*({rv['p'][1]}) = {rv['z']:.2f}")
    resultado['mensaje'] = f"La solución óptima es: {optimo['p'][0]:.2f} {vars_nombres['x']} y {optimo['p'][1]:.2f} {vars_nombres['y']} con la que se obtiene un {tipo_opt.upper()} de {optimo['z']:.2f}"
    
    #convertir la imagen a base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    resultado['img'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return resultado


def metodoSimplex(problemaPL):
    """
    Método iterativo para resolver modelos de programación lineal (Simplex / Dos Fases o Gran M).
    Se usa Pandas para mostrar la tabla iterativa con formato ASCII.
    """
    vars_nombres = problemaPL["variables"]
    restricciones = problemaPL["restricciones"]
    fo = problemaPL["funcion_objetivo"]
    tipo_opt = fo["tipo"].lower()

    vars_keys = list(vars_nombres.keys())
    num_vars = len(vars_keys)
    num_res = len(restricciones)

    holguras = []
    artificiales = []
    M = 1e7  # Gran M para penalizar artificiales

    for i, r in enumerate(restricciones):
        if r["signo"] == "<=":
            holguras.append(f"S{i+1}")
        elif r["signo"] == ">=":
            holguras.append(f"E{i+1}")
            artificiales.append(f"A{i+1}")
        elif r["signo"] == "=":
            artificiales.append(f"A{i+1}")

    cols = vars_keys + holguras + artificiales + ["R"]
    num_cols = len(cols)

    tabla = np.zeros((num_res + 1, num_cols))
    z_row = num_res

    # Fila Z inicial
    for j, vk in enumerate(vars_keys):
        val = fo.get(vk, 0)
        tabla[z_row, j] = -val if tipo_opt == "max" else val

    base = []
    cb = []

    h_idx = 0
    a_idx = 0
    for i, r in enumerate(restricciones):
        for j, vk in enumerate(vars_keys):
            tabla[i, j] = r.get(vk, 0)

        tabla[i, -1] = r["valor"]

        if r["signo"] == "<=":
            tabla[i, num_vars + h_idx] = 1
            base.append(holguras[h_idx])
            cb.append(0)
            h_idx += 1
        elif r["signo"] == ">=":
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
        elif r["signo"] == "=":
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
    resultado = {}

    def guardar_iteracion(entra,sale,pivote,razon_minima):
        iteracion = {
            "entra": entra,
            "sale": sale,
            "elemento_pivote": pivote,
            "razon_minima": razon_minima,
            "tabla": tabla_ant,
        }
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
    
    resultado["iteraciones"] = iteraciones

    # --- Resultados finales ---
    z_val = tabla[z_row, -1]
    if tipo_opt == "min":
        z_val = -z_val

    solucion = {"valores_fo": {"Z": fmt(z_val)}}
    for vk in vars_keys:
        val = tabla[base.index(vk), -1] if vk in base else 0
        solucion["valores_fo"][vk] = fmt(val)

    vars_optimas = [f"{fmt(solucion['valores_fo'][vk])} de {vars_nombres[vk]}" for vk in vars_keys]
    #Crear mensaje general para cualquier problema: 
    solucion["mensaje"] = (
        f"La solución óptima {tipo_opt.upper()} es: Z = {solucion['valores_fo']['Z']} "
        + f"y para obtenerla se debe hacer "
        + ", ".join(vars_optimas)
    )
    funcion_objetivo = f"{tipo_opt.upper()} Z = "
    for key, value in fo.items():
        if key != "tipo":
            funcion_objetivo += f"{value}{key} + "
    
    resultado["funcion_objetivo"] = funcion_objetivo.strip().rstrip('+').strip()
    resultado["solucion_optima"] = solucion
    return resultado