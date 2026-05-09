# SimplexPro

**SimplexPro** es una herramienta en Python diseñada para resolver problemas de **Programación Lineal** mediante el **Método Gráfico** (para 2 variables) y el **Método Simplex** (para N variables). Ofrece una API RESTful construida con FastAPI, almacenamiento en SQLite y generación de reportes en PDF.

---

## Características

- **API REST con FastAPI**: Endpoints estructurados para operaciones CRUD y resolución.
- **Resolución por Método Gráfico**: Encuentra automáticamente los vértices de la región factible y visualiza el problema (soporta exportación a PDF).
- **Resolución por Método Simplex**:
  - Soporte para **Maximización y Minimización**.
  - Manejo de restricciones `<=`, `>=` e `=`.
  - Implementación del método de la **Gran M (Big-M)** para variables artificiales.
  - Retorno detallado de cada tabla iterativa.
- **Validación Robusta**: Uso de **Pydantic V2** para validar esquemas y datos JSON.
- **Persistencia**: Base de datos asíncrona SQLite (`aiosqlite`) para guardar problemas y sus resultados.
- **Visualización**: Gráficos generados con `matplotlib` y convertidos a **Base64** para transmisión web.

---

## Tecnologías

- **Web Framework**: FastAPI (Async)
- **Gestor de dependencias**: uv
- **Base de Datos**: SQLite (aiosqlite)
- **Cálculo Numérico**: NumPy
- **Visualización**: Matplotlib
- **Generación PDF**: fpdf2

---

## Estructura del Proyecto

Arquitectura modular por capas:
```
simplexPro/
├── main.py                 # Entry point de FastAPI
├── app/
│   ├── db/                 # Conexión DB y operaciones CRUD
│   ├── schemas/            # Modelos Pydantic (Validación)
│   ├── services/           # Lógica de negocio (Gráfico, Simplex, Exportador)
│   ├── validators/         # Validaciones específicas del dominio
│   └── routes/             # Endpoints (resolución, problemas, utilidad)
```

---

## Instalación y Ejecución

Este proyecto utiliza `uv` para una gestión de dependencias rápida y eficiente.

### 1. Instalar dependencias
```bash
uv sync
```

### 2. Ejecutar la API
El servidor de desarrollo se inicia con FastAPI:
```bash
uv run fastapi dev main.py
```
La API estará disponible en `http://127.0.0.1:8000`.
Documentación interactiva Swagger: `http://127.0.0.1:8000/docs`.

---

## Estructura del Problema (JSON)

Ejemplo de payload aceptado por los endpoints (`/grafico` o `/simplex`):

```json
{
    "titulo": "Problema de ejemplo",
    "descripcion": "Descripción opcional",
    "variables": {"x": "Producto A", "y": "Producto B"},
    "restricciones": [
        {"x": 1, "y": 6, "signo": "<=", "valor": 20},
        {"x": 1, "y": 1, "signo": "<=", "valor": 60}
    ],
    "funcion_objetivo": {"x": 2, "y": 5, "tipo": "max"}
}
```

---

## Próximos Pasos

- Interfaz web interactiva con **React**.
- Exportación de resultados a formato Excel.