# SimplexPro

**SimplexPro** es una herramienta en Python diseñada para resolver problemas de **Programación Lineal** mediante el **Método Gráfico** (para 2 variables) y próximamente el **Método Simplex**.

---

## Características

- **Resolución por Método Gráfico**: Encuentra automáticamente los vértices de la región factible.
- **Visualización**: Gráficos claros con `matplotlib` que muestran:
  - Líneas de restricciones.
  - Región factible sombreada.
  - Vértices con sus respectivos valores de Z.
  - Punto óptimo resaltado.
- **Soporte para Maximización y Minimización**.
- **Entrada Estructurada**: Fácil definición de problemas mediante diccionarios de Python.

---

## Tecnologías

- **Gestor de dependencias**: uv
- **Cálculo Numérico**: NumPy
- **Visualización**: Matplotlib

---

## Instalación y Ejecución

Este proyecto utiliza `uv` para una gestión de dependencias rápida y eficiente.

### 1. Instalar dependencias
```bash
uv sync
```

### 2. Ejecutar la aplicación
```bash
uv run main.py
```

---

## Uso

Actualmente, el proyecto se centra en la función `metodoGrafico`. Para resolver un problema, se debe definir un diccionario con la siguiente estructura:

### Estructura del Problema
```python
problema = {
    "variables": {"x": "Nombre X", "y": "Nombre Y"},
    "restricciones": [
        {"x": coef_x, "y": coef_y, "signo": "<=" | ">=", "valor": constante},
        # ... más restricciones
    ],
    "funcion_objetivo": {"x": coef_x, "y": coef_y, "tipo": "max" | "min"},
}
```

### Ejemplo: Maximización de Utilidades
Un agricultor quiere maximizar su utilidad sembrando maíz (x) y cebada (y):

```python
problema = {
    "variables": {"x": "hectáreas de maíz", "y": "hectáreas de cebada"},
    "restricciones": [
        {"x": 1, "y": 1, "signo": "<=", "valor": 600},
        {"x": 1, "y": 2, "signo": "<=", "valor": 800},
        {"x": 1, "y": 0, "signo": ">=", "valor": 0},
        {"x": 0, "y": 1, "signo": ">=", "valor": 0}
    ],
    "funcion_objetivo": {"x": 60, "y": 70, "tipo": "max"},
}

metodoGrafico(problema)
```

---

## Estructura del Código

El archivo principal `main.py` contiene:

- **`metodoGrafico(problemaPL)`**: Función núcleo que:
  1. Calcula todas las intersecciones posibles entre restricciones.
  2. Filtra aquellas que cumplen con todas las restricciones (vértices factibles).
  3. Evalúa la función objetivo en cada vértice.
  4. Genera el reporte en consola y la representación gráfica.

---

## Próximos Pasos

- Implementación del **Método Simplex** para problemas de N variables.
- Creación de una API con **FastAPI**.
- Interfaz web con **React**.

---