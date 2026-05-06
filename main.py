import numpy as np
import matplotlib.pyplot as plt

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
        print("Error: No se encontró una región factible.")
        return

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

    # Salida
    print("\n" + "="*40)
    print(f" RESULTADOS FINALES ({tipo_opt.upper()})")
    print("="*40)
    for i, rv in enumerate(resultados):
        print(f"Vértice {i+1}: x={round(rv['p'][0])}, y={round(rv['p'][1])} | Z={rv['z']:.1f}")
    print("-" * 40)
    print(f"PUNTO ÓPTIMO: ({optimo['p'][0]:.2f}, {optimo['p'][1]:.2f})")
    print(f"VALOR Z MÁXIMO: {optimo['z']:.2f}")
    print("="*40 + "\n")

    plt.show()

# Un agricultor tiene 600 hectáreas en las que puede sembrar maíz o cebada y dispone de 800 horas de trabajo durante la temporada. 
# Los márgenes de utilidad por hectárea para el maíz son de 60€ y para la cebada es de 70€. Los requerimientos laborales para trabajar en la siembra de maíz es de 1 hora por hectárea y en la siembra de cebada es de 2 horas por hectárea. 
# ¿Cuántas hectáreas de cada cultivo debe sembrar para maximizar su utilidad?, ¿Cuál es la utilidad máxima?

problemaPL2 = {
    "variables": {"x": "nº de hectáreas de maíz", "y": "nº de hectáreas de cebada"},
    "restricciones": [
        {"x": 1, "y": 1, "signo": "<=", "valor": 600},
        {"x": 1, "y": 2, "signo": "<=", "valor": 800},
        # Definimos las restricciones de no negatividad (x >= 0, y >= 0)
        {"x": 1, "y": 0, "signo": ">=", "valor": 0},
        {"x": 0, "y": 1, "signo": ">=", "valor": 0}
    ],
    "funcion_objetivo": {"x": 60, "y": 70, "tipo": "max"},
}

# Una empresa decide, por el día del trabajador, llevar de paseo a la playa a 400 trabajadores (por lo menos). 
# Para ello contrata a una compañía de transporte, la cual dispone de autobuses para 60 pasajeros y microbuses para 20 pasajeros. 
# El precio de alquiler de cada autobús es de 250€ y de cada microbús de 200€. 
# La compañía de transporte solo dispone ese día de 8 choferes profesionales. 
# ¿Qué número de autobuses y microbuses deben contratarse para que el costo sea mínimo?

problemaPL = {
    "variables": {"x": "nº de autobuses", "y": " nº de microbuses"},
    "restricciones": [
        {"x": 60, "y": 20, "signo": ">=", "valor": 400},
        {"x": 1, "y": 1, "signo": "<=", "valor": 8},
        {"x":1, "y": 0, "signo": ">=", "valor": 0},
        {"x": 0, "y": 1, "signo": ">=", "valor": 0}
    ],
    "funcion_objetivo": {"x": 250, "y": 200, "tipo": "min"},
}


if __name__ == "__main__":
    metodoGrafico(problemaPL)
    metodoGrafico(problemaPL2)