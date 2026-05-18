import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from app.schemas.resultados import ResultadoGrafico
from app.schemas.problemaPL import ProblemaPL, Restriccion

def metodoGrafico(problemaPL: ProblemaPL) -> ResultadoGrafico:
    """
    Metodo grafico para resolver problemas de Programación Lineal de 2 variables.
    """
    vars_nombres = problemaPL.variables
    restricciones = problemaPL.restricciones.copy()
    
    # Restricciones de no negatividad
    restricciones.append(Restriccion(x=1, y=0, signo=">=", constante=0))
    restricciones.append(Restriccion(x=0, y=1, signo=">=", constante=0))
    
    fo = problemaPL.funcion_objetivo
    tipo_opt = fo.tipo.lower()

    def _fmt_num(n):
        """Formatea números para no mostrar decimales innecesarios."""
        if isinstance(n, float) and abs(n) < 1e-8:
            return 0
        rounded = round(float(n), 2)
        return int(rounded) if rounded == int(rounded) else rounded

    def interseccion(r1: Restriccion, r2: Restriccion):
        """Resuelve el sistema de ecuaciones entre dos rectas."""
        a = np.array([[r1.x, r1.y], [r2.x, r2.y]])
        b = np.array([r1.constante, r2.constante])
        try:
            return np.linalg.solve(a, b)
        except np.linalg.LinAlgError:
            return None

    def es_factible(p, lista_res):
        """Filtro CRUCIAL: Verifica que el punto satisfaga TODAS las restricciones."""
        x, y = p
        margen = 1e-7 # Tolerancia para errores de punto flotante
        for r in lista_res:
            val = r.x * x + r.y * y
            if r.signo == "<=" and val > r.constante + margen: return False
            if r.signo == ">=" and val < r.constante - margen: return False
            if r.signo == "=" and not np.isclose(val, r.constante, atol=margen): return False
        return True

    # --- PASO 2: Hallar Vértices de la Región Factible ---
    puntos_v = []
    n = len(restricciones)
    for i in range(n):
        for j in range(i+1, n):
            p = interseccion(restricciones[i], restricciones[j])
            if p is not None and es_factible(p, restricciones):
                # Validar que no esté duplicado
                if not any(np.allclose(p, v, atol=1e-5) for v in puntos_v):
                    puntos_v.append(p)

    # --- PASO 3: Evaluación de la Función Objetivo ---
    valoresFactibles = []
    optimo = None
    if puntos_v:
        for v in puntos_v:
            px, py = v[0], v[1]
            z = fo.x * px + fo.y * py
            valoresFactibles.append({'p': np.array([px, py]), 'z': z})

        # Buscar el óptimo según sea MAX o MIN
        if tipo_opt == "max":
            optimo = max(valoresFactibles, key=lambda x: x['z'])
        else:
            optimo = min(valoresFactibles, key=lambda x: x['z'])
        
        
        # Poblar mensajes de éxito en el objeto Resultado
        valoresFO = []
        for rv in valoresFactibles:
            tipo = f" ({tipo_opt.upper()})" if np.isclose(rv['z'], optimo['z']) else ""
            valoresFO.append(
                f"Z({_fmt_num(rv['p'][0])}, {_fmt_num(rv['p'][1])}) = {_fmt_num(fo.x)}·({_fmt_num(rv['p'][0])}) + {_fmt_num(fo.y)}·({_fmt_num(rv['p'][1])}) = {_fmt_num(rv['z'])} {tipo}"
            )
        tipo_texto = "máximo" if tipo_opt == "max" else "mínimo"
        x = optimo['p'][0]
        x = f"{round(x):,}" if _fmt_num(x) == round(x) else f"{_fmt_num(optimo['p'][0]):,} ≈ {round(optimo['p'][0]):,}"
        y = optimo['p'][1]
        y = f"{round(y):,}" if _fmt_num(y) == round(y) else f"{_fmt_num(optimo['p'][1]):,} ≈ {round(optimo['p'][1]):,}"
        mensaje = f"La solución óptima es {x} ({vars_nombres['x']}) y {y} ({vars_nombres['y']}), con un valor {tipo_texto} de Z = {_fmt_num(optimo['z']):,}"
    else:
        mensaje = "No se encontró una región factible. Las restricciones son incompatibles."
    # --- PASO 4: Visualización Gráfica ---
    plt.figure(figsize=(11, 7))
    ax = plt.gca()
    # Límites dinámicos para una buena visualización, incluso si no es factible
    if puntos_v:
        max_x = max([v[0] for v in puntos_v] + [10]) * 1.2
        max_y = max([v[1] for v in puntos_v] + [10]) * 1.2
    else:
        cortes = []
        for r in restricciones:
            if r.x != 0: cortes.append(r.constante / r.x)
            if r.y != 0: cortes.append(r.constante / r.y)
        max_corte = max(cortes) if cortes else 10
        max_x = max_y = max(max_corte, 10) * 1.2

    x_rango = np.linspace(0, max_x, 500)

    # Dibujar líneas de TODAS las restricciones
    for i, res in enumerate(restricciones[:-2]): # Excluimos las de no negatividad para no saturar los ejes
        etiqueta = f"R{i+1}: {_fmt_num(res.x)}x + {_fmt_num(res.y)}y {res.signo} {_fmt_num(res.constante)}"
        if res.y != 0:
            if res.x == 0:
                plt.axhline(y=res.constante / res.y, label=etiqueta, linewidth=2)
            else:
                y_r = (res.constante - res.x * x_rango) / res.y
                plt.plot(x_rango, y_r, label=etiqueta, linewidth=2)
        else:
            plt.axvline(x=res.constante / res.x, label=etiqueta, linewidth=2)

    if puntos_v:
        # Dibujar Región Factible según la geometría
        if len(puntos_v) >= 3:
            # Polígono tradicional (Sombra)
            centro = np.mean(puntos_v, axis=0)
            puntos_v_ord = sorted(puntos_v, key=lambda p: np.arctan2(p[1]-centro[1], p[0]-centro[0]))
            poligono = plt.Polygon(puntos_v_ord, color='green', alpha=0.15, label='Región Factible')
            ax.add_patch(poligono)
        elif len(puntos_v) == 2:
            # Segmento de recta (Común en restricciones con '=')
            plt.plot([puntos_v[0][0], puntos_v[1][0]], [puntos_v[0][1], puntos_v[1][1]], color='green', linewidth=5, alpha=0.5, label='Región Factible (Segmento)')
        elif len(puntos_v) == 1:
            # Un solo punto posible
            plt.plot(puntos_v[0][0], puntos_v[0][1], 'go', markersize=10, alpha=0.5, label='Región Factible (Punto)')
        # Dibujar vértices evaluados
        for res_v in valoresFactibles:
            v = res_v['p']
            plt.plot(v[0], v[1], 'ko', markersize=5, zorder=4)
            offset = max_x * 0.015
            plt.text(v[0]+offset, v[1]+offset, f"({v[0]:.1f}, {v[1]:.1f})\nZ={res_v['z']:,.0f}", fontsize=8, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        # MARCAR EL ÓPTIMO
        plt.scatter(optimo['p'][0], optimo['p'][1], color='red', marker='*', s=350, edgecolor='black', label=f'SOLUCIÓN ÓPTIMA', zorder=10)
    else:
        # Marca de agua si las restricciones son incompatibles (No sombrea nada)
        plt.text(max_x/2, max_y/2, 'SIN REGIÓN FACTIBLE\n(Restricciones incompatibles)', fontsize=20, color='red', alpha=0.4, ha='center', va='center', fontweight='bold', rotation=30)

    # Configuración de ejes y estética
    plt.axhline(0, color='black', linewidth=1.5, zorder=3)
    plt.axvline(0, color='black', linewidth=1.5, zorder=3)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(-0.5, max_x)
    plt.ylim(-0.5, max_y)
    plt.xlabel(vars_nombres.get('x', 'x'))
    plt.ylabel(vars_nombres.get('y', 'y'))
    plt.title(f"Método Gráfico - Optimización {tipo_opt.upper()}", fontsize=14)
    plt.legend(loc='upper right', fontsize=9)

    # Convertir gráfico a Base64 para retornar
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    grafico = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    resultado = ResultadoGrafico(
        valoresFO=valoresFO,
        funcion_objetivo=f"{tipo_opt.upper()} Z = {fo.x}x + {fo.y}y",
        mensaje=mensaje,
        grafico=grafico,
    )

    return resultado