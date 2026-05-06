import numpy as np
import sys

# Forzar salida en UTF-8 para evitar errores con caracteres de caja en Windows
sys.stdout.reconfigure(encoding='utf-8')
import matplotlib.pyplot as plt
import pandas as pd

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

    def print_tabla(iteracion, tabla, base, cb, entra=None, sale=None, pivote=None):
        print(f"\n" + "="*50)
        print(f" ITERACIÓN {iteracion}")
        print("="*50)
        if entra and sale:
            print(f"Entra: {entra} | Sale: {sale} | Elemento pivote: {pivote:.2f}")
            
        df = pd.DataFrame(tabla, columns=cols)
        df.insert(0, "Base", base + ["Z"])
        
        # Cb column (costes)
        cb_str = [f"{c:.0f}" if abs(c) < M else ("-M" if c < 0 else "M") for c in cb] + ["-"]
        df.insert(0, "Cb", cb_str)

        # Truncar números muy pequeños a 0 para limpieza visual
        df[cols] = df[cols].map(lambda x: 0.0 if abs(x) < 1e-8 else x)
        
        # Para evitar valores M en la impresión de R en la fila Z
        df["R"] = df["R"].astype(object)
        if abs(df.at[z_row, "R"]) > M / 10:
             val_z = df.at[z_row, "R"]
             if val_z > 0: df.at[z_row, "R"] = f"{val_z/M:.2f}M"
             else: df.at[z_row, "R"] = f"{val_z/M:.2f}M"
        
        df_str = df.round(2).astype(str)
        str_lines = df_str.to_string(index=False).split('\n')
        ancho = max(len(line) for line in str_lines) + 2
        
        print("┌" + "─" * ancho + "┐")
        for line in str_lines:
            print(f"│ {line:<{ancho-1}}│")
        print("└" + "─" * ancho + "┘")

    iteracion = 0
    print_tabla(iteracion, tabla, base, cb)

    while True:
        z_vals = tabla[z_row, :-1]
        
        if tipo_opt == "max":
            if np.all(z_vals >= -1e-8):
                break
            col_pivote = np.argmin(z_vals)
        else:
            if np.all(z_vals <= 1e-8):
                break
            col_pivote = np.argmax(z_vals)
            
        col_vals = tabla[:-1, col_pivote]
        rhs = tabla[:-1, -1]
        ratios = np.full(num_res, np.inf)
        
        for i in range(num_res):
            if col_vals[i] > 1e-8:
                ratios[i] = rhs[i] / col_vals[i]
                
        if np.all(ratios == np.inf):
            print("\nError: Problema no acotado.")
            return
            
        fila_pivote = np.argmin(ratios)
        pivote = tabla[fila_pivote, col_pivote]
        
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
            
        iteracion += 1
        print_tabla(iteracion, tabla, base, cb, entra, sale, pivote)

    print("\n" + "="*50)
    print(" RESULTADOS FINALES SIMPLEX")
    print("="*50)
    z_val = tabla[z_row, -1]
    if tipo_opt == "min":
        z_val = -z_val
    print(f"Z = {z_val:,.2f}")
    
    for vk in vars_keys:
        val = tabla[base.index(vk), -1] if vk in base else 0
        print(f"{vk.upper()} = {val:,.2f} ({vars_nombres[vk]})")
        
    for hk in holguras:
        val = tabla[base.index(hk), -1] if hk in base else 0
        print(f"{hk} = {val:,.2f}")
    print("="*50 + "\n")
    

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

"""
Ejemplo 1:
Función Objetivo
Maximizar: Z = 2X1 + 5X2

Sujeto a:
X1 + 6X2 ≤ 20

X1 + X2 ≤ 60

X1  ≤ 40

X1, X2 ≥ 0
"""

problemaPL3 = {
    "variables": {"x1": "productoA", "x2": "productoB"},
    "restricciones": [
        {"x1": 1, "x2": 6, "signo": "<=", "valor": 20},
        {"x1": 1, "x2": 1, "signo": "<=", "valor": 60},
        {"x1": 1, "x2": 0, "signo": "<=", "valor": 40}
    ],
    "funcion_objetivo": {"x1": 2, "x2": 5, "tipo": "max"},
}

"""
Ejemplo 2:
Función objetivo
Maximizar: Z= 5000 X1 + 6500 X2 + 9000 X3 + 1200 X4
Sujeto a:
X1 ≤ 8
X2 ≤ 15
X3 ≤ 15
X4 ≤ 11
800 X1 + 926 X2 + 290 X3 + 480 X4 ≤ 8500
X3 + X4 ≤ 5
280 X3 + 390 X4 ≤ 1700
"""

problemaPL4 = {
    "variables": {"x1": "productoA", "x2": "productoB", "x3": "productoC", "x4": "productoD"},
    "restricciones": [
        {"x1": 1, "x2": 0, "x3": 0, "x4": 0, "signo": "<=", "valor": 8},
        {"x1": 0, "x2": 1, "x3": 0, "x4": 0, "signo": "<=", "valor": 15},
        {"x1": 0, "x2": 0, "x3": 1, "x4": 0, "signo": "<=", "valor": 15},
        {"x1": 0, "x2": 0, "x3": 0, "x4": 1, "signo": "<=", "valor": 11},
        {"x1": 800, "x2": 926, "x3": 290, "x4": 480, "signo": "<=", "valor": 8500},
        {"x1": 0, "x2": 0, "x3": 1, "x4": 1, "signo": "<=", "valor": 5},
        {"x1": 0, "x2": 0, "x3": 280, "x4": 390, "signo": "<=", "valor": 1700}
    ],
    "funcion_objetivo": {"x1": 5000, "x2": 6500, "x3": 9000, "x4": 1200, "tipo": "max"},
}


"""
Ejercicio propuesto 1
Un joven empresario pretende abrir un local en el centro de la ciudad
para atender a tres tipos de perros A, B y C, los cuales deben pasar por los
cuartos de baño, secado y peluquería. Se ha estimado que el tiempo en
horas de cada perro en cada cuarto es el expresado en la Tabla 4. Así mismo
se establece la utilidad que genera cada perro después de la operación en
miles de pesos colombianos.

Tiempo en horas                                | Utilidad en pesos
-------------------------------------------------------------------
Perro            | Baño  | Secado | Peluquería |  colombianos ($)
--------------------------------------------------------------------
A                  | 1     | 1      | 2          | $ 60.000
B                  | 2     | 1      | 2          | $ 70.000
C                  | 3     | 1      | 3          | $ 80.000 

El empresario decide limitar el tiempo de servicio a 110 horas para baños, 
120 horas para secado y 180 horas para peluquería. ¿Cuántos perros de cada tipo 
debe atender para maximizar su utilidad?

El tiempo disponible para los tres cuartos será de 72 horas semanales
¿A qué cantidad de cada tipo de perro A, B y C debe el local prestar el
servicio para maximizar las ganancias? Si se espera prestar el servicio por
lo menos a 10 perros del tipo C por semana.
—Formulación del modelo
Variables de decisión
X1 = Perro tipo A
X2 = Perro tipo B
X3 = Perro tipo C
—Función objetivo
Maximizar Z= $60.000X1 +$70.000X2 +$80.000X3
Sujeto a:
X1 + 2X2 + 3X3 ≤ 72
(Horas máximas disponibles del cuarto de baño)
X1 + X2 + X3 ≤ 72
(Horas máximas disponibles del cuarto de secado)
2X1 + 2X2 + 3X3 ≤ 72
(Horas máximas disponibles del cuarto de peluquería)
X3 ≥ 10
(Número de perros tipo C mínimos para prestar el servicio por semana)
X1, X2, X3 ≥ 0
"""

problemaPL5 = {
    "variables": {"x1": "perroA", "x2": "perroB", "x3": "perroC"},
    "restricciones": [
        {"x1": 1, "x2": 2, "x3": 3, "signo": "<=", "valor": 72},
        {"x1": 1, "x2": 1, "x3": 1, "signo": "<=", "valor": 72},
        {"x1": 2, "x2": 2, "x3": 3, "signo": "<=", "valor": 72},
        {"x1": 0, "x2": 0, "x3": 1, "signo": ">=", "valor": 10}
    ],
    "funcion_objetivo": {"x1": 60000, "x2": 70000, "x3": 80000, "tipo": "max"},
}

"""
Ejercicio propuesto 2
Una empresa de labiales ha sacado a la venta tres tipos de colores:
morado, rosado y rojo. Estos labiales tienen una utilidad de $100 pesos
colombianos cada uno. La producción mensual solo puede llegar hasta
500 unidades de labiales. Se conoce que las mujeres prefieren el labial
rojo con mayor frecuencia, debido a esto la compañía ha estimado
producir mensualmente mínimo 250 unidades de labiales rojos,
máximo 100 unidades de labiales morados.

Debido a la mala administración de las ventas y a los respectivos
pronósticos, la empresa en el último mes ha producido labiales de
referencias no demandadas con mayor frecuencia, razón por la cual se
ha generado inventario de productos en el almacén. Por este motivo la
empresa quiere conocer cuál es la cantidad de cada labial a producir
para maximizar las ganancias. También desea saber cómo superar las
ganancias de la producción del mes pasado que fueron de $30.000 pesos
colombianos.

Formulación del modelo
Variables de decisión
X1 = Labiales Morados
X2 = Labiales rosados
X3 = Labiales rojos
Función objetivo
Maximizar Z= 100X1 + 100X2 + 100X3
Sujeto a
X1 + X2 + X3 = 500
(Cantidad de unidades a producir mensualmente)
X3 ≥ 250
(Producción mínima de labial rojo)
X1 ≤ 100
(Producción máxima de labial morado)
X1 + X2 + X3 ≥ 30000
(Utilidad minina mensual en pesos colombianos)
X1 + X2 + X3 ≥ 0
"""

problemaPL6 = {
    "variables": {"x1": "labialesMorados", "x2": "labialesRosados", "x3": "labialesRojos"},
    "restricciones": [
        {"x1": 1, "x2": 1, "x3": 1, "signo": "=", "valor": 500},
        {"x1": 0, "x2": 0, "x3": 1, "signo": ">=", "valor": 250},
        {"x1": 1, "x2": 0, "x3": 0, "signo": "<=", "valor": 100},
        {"x1": 100, "x2": 100, "x3": 100, "signo": ">=", "valor": 30000},
        {"x1": 1, "x2": 1, "x3": 1, "signo": ">=", "valor": 0}
    ],
    "funcion_objetivo": {"x1": 100, "x2": 100, "x3": 100, "tipo": "max"},
}

if __name__ == "__main__":
    # --- Resultados Esperados para problemaPL3, problemaPL4, problemaPL5, problemaPL6 ---
    metodoSimplex(problemaPL3)
    # Z = 40
    # X1= 20, X2= 0, S1= 0, S2= 40, S3= 20
    
    metodoSimplex(problemaPL4)
    # Z = 944.870
    # X1 = 0
    # X2 = 7.61
    # X3 = 5
    
    metodoSimplex(problemaPL5)
    # Las ncias de la empresa debe ofertar el servicio a perros del tipo B y C, para
    # atender un total de 21 perros del tipo B y 10 perros del tipo C, obteniendo
    # así una ganancia de $2´270.000 pesos colombianos semanales.
    # Z= 2270000
    # X1= 0, X2=21, X3=10
    

    metodoSimplex(problemaPL6)
    # ―Solución óptima: La empresa para maximizar ganancias debe
    # producir una cantidad de 100 unidades de labiales morados, 150 unidades
    # de labiales rosados y de labiales rojos un total de 250 unidades. De este
    # modo se podría obtener una utilidad de $50.000 pesos colombianos, lo
    # cual representa una diferencia favorable de $20.000 pesos colombianos
    # respecto al mes pasado.
    # Z = 50000
    # X1 = 100
    # X2 = 150
    # X3 = 250
