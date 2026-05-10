import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from app.schemas.grafico_model import ProblemaPL, Restriccion

def metodoGrafico(problemaPL:ProblemaPL):
    """
    Metodo grafico para resolver problemas de Programación Lineal de 2 variables.
    """
    vars_nombres = problemaPL.variables
    restricciones = problemaPL.restricciones
    fo = problemaPL.funcion_objetivo
    tipo_opt = fo.tipo.lower()

    def interseccion(r1:Restriccion, r2:Restriccion):
        """Resuelve el sistema de ecuaciones entre dos rectas."""
        a = np.array([[r1.x, r1.y], [r2.x, r2.y]])
        b = np.array([r1.valor, r2.valor])
        try:
            return np.linalg.solve(a, b)
        except np.linalg.LinAlgError:
            return None

    def es_factible(p, lista):
        x, y = p 
        margen = 1e-8
        for r in lista:
            val = r.x*x + r.y*y
            if r.signo == "<=" and val > r.valor + margen: return False
            if r.signo == ">=" and val < r.valor - margen: return False
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
        # Validar si son enteros y redondear si no lo son
        if v[0] % 1 != 0: 
            v[0] = round(v[0])
        if v[1] % 1 != 0:
            v[1] = round(v[1])
        z = fo.x*v[0] + fo.y*v[1]
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
        etiqueta = f"R{i+1}: {res.x}x + {res.y}y {res.signo} {res.valor}"
        if res.y != 0:
            y_r = (res.valor - res.x*x_rango) / res.y
            plt.plot(x_rango, y_r, label=etiqueta, linewidth=2)
        else:
            plt.axvline(res.valor/res.x, label=etiqueta, linewidth=2)

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
    plt.xlabel(vars_nombres.x)
    plt.ylabel(vars_nombres.y)
    plt.title(f"Método Gráfico - Optimización {tipo_opt.upper()} Z = {fo.x}x + {fo.y}y", fontsize=14)
    plt.legend(loc='upper right', fontsize=9)

    # Guardar resultados
    resultado = {"valores_fo":[]}
    resultado['funcion_objetivo'] = f"{fo.x}x + {fo.y}y"
    tipo = ""
    for i, rv in enumerate(resultados):
        if rv['z'] == optimo['z']:
            tipo = tipo_opt.upper()
        else:
            tipo = ""
        resultado['valores_fo'].append(f"f({rv['p'][0]:.0f}, {rv['p'][1]:.0f}) = {fo.x}*({rv['p'][0]:.0f}) + {fo.y}*({rv['p'][1]:.0f}) = {rv['z']:,.2f} " + tipo)                  
    resultado['mensaje'] = f"La solución óptima es: {optimo['p'][0]:,.0f} {vars_nombres['x']} y {optimo['p'][1]:,.0f} {vars_nombres['y']} con la que se obtiene un {tipo_opt.upper()} de {optimo['z']:,.2f}"
    
    #convertir la imagen a base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    resultado['img'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return resultado
