# SimplexPro

**SimplexPro** es una herramienta en Python diseñada para resolver problemas de **Programación Lineal** mediante el **Método Gráfico** (para 2 variables) y el **Método Simplex** (para N variables).

---

## Características

- **Resolución por Método Gráfico**: Encuentra automáticamente los vértices de la región factible y visualiza el problema.
- **Resolución por Método Simplex**:
  - Soporte para **Maximización y Minimización**.
  - Manejo de restricciones `<=`, `>=` e `=`.
  - Implementación del método de la **Gran M (Big-M)** para variables artificiales.
  - Generación de tablas iterativas detalladas en formato ASCII.
- **Visualización**: Gráficos claros con `matplotlib` para el método gráfico.
- **Entrada Estructurada**: Definición de problemas mediante diccionarios de Python.

---

## Tecnologías

- **Gestor de dependencias**: uv
- **Cálculo Numérico**: NumPy
- **Análisis de Datos**: Pandas (para tablas Simplex)
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

### Estructura del Problema
```python
# Ejemplo para Método Gráfico
problema = {
    "variables": {"x": "Nombre X", "y": "Nombre Y"},
    "restricciones": [
        {"x": coef_x, "y": coef_y, "signo": "<=" | ">=", "valor": constante},
        # ...
    ],
    "funcion_objetivo": {"x": coef_x, "y": coef_y, "tipo": "max" | "min"},
}

# Ejemplo para Método Simplex
problema = {
    "variables": {"x1": "Nombre Variable 1", "x2": "Nombre Variable 2", ...},
    "restricciones": [
        {"x1": coef1, "x2": coef2, "signo": "<=" | ">=" | "=", "valor": constante},
        # ...
    ],
    "funcion_objetivo": {"x1": coef1, "x2": coef2, "tipo": "max" | "min"},
}
```

### Ejemplo: Método Gráfico
Un agricultor tiene 600 hectáreas en las que puede sembrar maíz o cebada y dispone de 800 horas de trabajo durante la temporada. 
Los márgenes de utilidad por hectárea para el maíz son de 60€ y para la cebada es de 70€. Los requerimientos laborales para trabajar en la siembra de maíz es de 1 hora por hectárea y en la siembra de cebada es de 2 horas por hectárea. 
¿Cuántas hectáreas de cada cultivo debe sembrar para maximizar su utilidad?, ¿Cuál es la utilidad máxima?

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

### Ejemplo: Método Simplex
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

```python
problema = {
    "variables": {"x1": "productoA", "x2": "productoB", "x3": "productoC", "x4": "productoD"},
    "restricciones": [
        {"x1": 1, "x2": 0, "x3": 0, "x4": 0, "signo": "<=", "valor": 8},
        {"x1": 0, "x2": 1, "x3": 0, "x4": 0, "signo": "<=", "valor": 15},
        {"x1": 0, "x2": 0, "x3": 1, "x4": 0, "signo": "<=", "valor": 15},
        {"x1": 0, "x2": 0, "x3": 0, "x4": 1, "signo": "<=", "valor": 11},
        {"x1": 800, "x2": 926, "x3": 290, "x4": 480, "signo": "<=", "valor": 8500},
        {"x1": 0, "x2": 0, "x3": 1, "x4": 1, "signo": "<=", "valor": 5},
        {"x1": 0, "x2": 0, "x3": 280, "x4": 390, "signo": "<=", "valor": 1700},
    ],
    "funcion_objetivo": {"x1": 5000, "x2": 6500, "x3": 9000, "x4": 1200, "tipo": "max"},
}

metodoSimplex(problema)
```

---

## Estructura del Código

El archivo principal `main.py` contiene:

- **`metodoGrafico(problemaPL)`**: Resolución geométrica para 2 variables con visualización.
- **`metodoSimplex(problemaPL)`**: Algoritmo iterativo que utiliza Pandas para mostrar el proceso de optimización paso a paso, incluyendo:
  - Identificación de columna y fila pivote.
  - Operaciones de Gauss-Jordan.
  - Manejo de penalizaciones con la Gran M.

---

## Ejercicios de Prueba

El proyecto incluye varios casos de prueba documentados:
- **Ejemplos 1 y 2**: Problemas estándar de maximización.
- **Ejercicio Perros (PL5)**: Problema de maximización de utilidad con restricciones de tiempo y mínimos de servicio.
- **Ejercicio Labiales (PL6)**: Problema de optimización de producción con metas de utilidad y preferencias de mercado.

---

## Próximos Pasos

- Creación de una API con **FastAPI**.
- Interfaz web interactiva con **React**.
- Exportación de resultados a formatos PDF/Excel.

---