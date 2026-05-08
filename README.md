# SimplexPro

**SimplexPro** es una herramienta en Python diseñada para resolver problemas de **Programación Lineal** mediante el **Método Gráfico** (para 2 variables) y el **Método Simplex** (para N variables). 

---

## Características

- **Resolución por Método Gráfico**: Encuentra automáticamente los vértices de la región factible y visualiza el problema.
- **Resolución por Método Simplex**:
  - Soporte para **Maximización y Minimización**.
  - Manejo de restricciones `<=`, `>=` e `=`.
  - Implementación del método de la **Gran M (Big-M)** para variables artificiales.
  - Retorno detallado de cada tabla iterativa.
- **Preparado para API**: Las funciones principales retornan diccionarios compatibles con JSON.
- **Visualización**: Gráficos generados con `matplotlib` y convertidos a **Base64** para fácil transmisión web.

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

## Estructura del Código y Retorno JSON

El archivo principal `main.py` contiene las funciones núcleo que retornan estructuras de datos listas para JSON:

### `metodoGrafico(problemaPL)`
Retorna un diccionario con:
- `puntos`: Lista de todos los puntos de intersección evaluados.
- `optimo`: Punto que maximiza/minimiza la función.
- `mensaje`: Interpretación textual del resultado.
- `img`: Imagen del gráfico en formato **Base64**.

### `metodoSimplex(problemaPL)`
Retorna un diccionario con:
- `iteraciones`: Lista de objetos que representan cada paso del Simplex:
    - `tabla`: El estado de la matriz (incluyendo etiquetas de base, valores de Cb y columna R).
    - `entra` / `sale`: Variables que entran y salen de la base.
    - `elemento_pivote`: Valor del pivote utilizado.
    - `razon_minima`: Valor de la razón mínima para la salida.
- `optimo`: Resultados finales (valor de Z y variables de decisión).

---

## Uso

### Estructura del Problema
```python
# Ejemplo de entrada
problema = {
    "variables": {"x1": "Producto A", "x2": "Producto B"},
    "restricciones": [
        {"x1": 1, "x2": 6, "signo": "<=", "valor": 20},
        {"x1": 1, "x2": 1, "signo": "<=", "valor": 60}
    ],
    "funcion_objetivo": {"x1": 2, "x2": 5, "tipo": "max"},
}
```

### Ejemplo de Integración
```python
import json
from main import metodoSimplex

resultado = metodoSimplex(problema)
print(json.dumps(resultado, indent=4))
```

---

## Próximos Pasos

- Creación de una API REST con **FastAPI**.
- Interfaz web interactiva con **React**.
- Exportación de resultados a formatos PDF/Excel.

---