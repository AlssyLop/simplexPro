# SimplexPro

**SimplexPro** es una herramienta en Python para resolver problemas de **Programación Lineal** mediante el **Método Gráfico** (2 variables) y el **Método Simplex/Gran M** (N variables). Expone una API REST con FastAPI, persistencia en SQLite y generación de reportes PDF.

---

## Características

- **API REST con FastAPI**: Endpoints CRUD + resolución unificada vía query param.
- **Método Gráfico**: Encuentra vértices de la región factible, incluye restricciones de no-negatividad (`x ≥ 0`, `y ≥ 0`), gráfico matplotlib en base64 y exportación a PDF.
- **Método Simplex / Gran M**: Soporta maximización/minimización, restricciones `<=`, `>=`, `=`, variables artificiales con penalización Big-M, y retorna todas las iteraciones (tabla, pivote, entrada/salida).
- **Validación con Pydantic V2**: Esquemas tipados con validación automática.
- **Persistencia**: SQLite asíncrona (`aiosqlite`) con `RETURNING` para atomicidad.
- **PDF**: Reportes con fpdf2 (solución, vértices evaluados, gráfico).

---

## Tecnologías

| Componente | Librerias |
|-|-|
| Web Framework | FastAPI (async) |
| Gestor de dependencias | uv |
| Base de Datos | SQLite (aiosqlite) |
| Cálculo Numérico | NumPy |
| Visualización | Matplotlib |
| PDF | fpdf2 |

---

## Estructura del Proyecto

```
simplexPro/
├── main.py                     # Entry point FastAPI + lifespan
├── simplexPro.sql              # DDL de la base de datos
├── app/
│   ├── db/
│   │   └── connection.py       # Conexión async SQLite + DbDep
│   ├── schemas/
│   │   ├── problemaPL_model.py # Modelos base (ProblemaPL, Resultado, etc.)
│   │   ├── grafico_model.py    # Modelos para método gráfico
│   │   └── simplex_model.py    # Modelos para método simplex
│   ├── validators/
│   │   └── problema.py         # Validación de estructura del problema
│   ├── services/
│   │   ├── grafico.py          # Solver gráfico (2 variables)
│   │   ├── simplex.py          # Solver simplex / Gran M
│   │   └── exportador.py       # Generación de PDF
│   ├── repository/
│   │   ├── problemaPL_dao.py   # CRUD de problemaPL
│   │   ├── grafico_dao.py      # CRUD de metodoGrafico
│   │   └── simplex_dao.py      # CRUD de metodoSimple + iteraciones
│   └── routes/
│       ├── problemas.py        # Endpoints CRUD + resolución
│       └── utilidad.py         # Endpoint de exportación PDF
```

---

## Instalación y Ejecución

```bash
# 1. Sincronizar dependencias
uv sync

# 2. Iniciar servidor de desarrollo
uv run fastapi dev main.py
```

La API queda en `http://localhost:8000`.
Documentación Swagger: `http://localhost:8000/docs`.

---

## Endpoints de la API

### Gestión y Resolución (`/problema`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/problema/registrar?metodo=grafico\|simplex` | Registra un problema y lo resuelve |
| `PUT` | `/problema/actualizar?metodo=grafico\|simplex` | Actualiza un problema existente y lo resuelve |
| `GET` | `/problema/listar?page=1` | Lista problemas (10 por página) |
| `GET` | `/problema/solucion/grafica/{id}` | Obtiene solución gráfica guardada |
| `GET` | `/problema/solucion/simplex/{id}` | Obtiene solución simplex guardada |
| `DELETE` | `/problema/eliminar/{id}` | Elimina un problema |

### Utilidad

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/problemas/{id}/exportar` | Exporta PDF con solución gráfica |

---

## Ejemplos de Uso

### Método Gráfico (2 variables)

```json
POST /problema/registrar?metodo=grafico
{
    "titulo": "Problema de ejemplo",
    "descripcion": "Optimizar producción",
    "variables": { "x": "Producto A", "y": "Producto B" },
    "restricciones": [
        { "x": 2, "y": 3, "signo": "<=", "valor": 100, "glosa": "Materia prima" },
        { "x": 1, "y": 2, "signo": "<=", "valor": 80, "glosa": "Mano de obra" }
    ],
    "funcion_objetivo": { "x": 50, "y": 40, "tipo": "max" }
}
```

### Método Simplex (N variables)

```json
POST /problema/registrar?metodo=simplex
{
    "titulo": "Problema simplex",
    "descripcion": "Optimizar producción",
    "variables": { "x1": "Producto A", "x2": "Producto B", "x3": "Producto C", "xn" ...},
    "restricciones": [
        { "x1": 2, "x2": 1, "x3": 3, "signo": "<=", "valor": 100, "glosa": "Materia prima" },
        { "x1": 1, "x2": 2, "x3": 1, "signo": ">=", "valor": 50, "glosa": "Mano de obra" }
    ],
    "funcion_objetivo": { "x1": 30, "x2": 20, "x3": 50, "tipo": "max" }
}
```

---

## Esquema de la Base de Datos

- `problemaPL` — Problemas registrados (UUID, título, FO, tipo optimización).
- `variables` — Variables asociadas a cada problema.
- `restricciones` — Restricciones con inecuación y glosa.
- `metodoGrafico` — Resultados gráficos (vértices, mensaje, gráfico PNG en BLOB).
- `metodoSimple` — Resultados simplex (valor FO, mensaje).
- `iteracionSimple` — Cada iteración del simplex (tabla JSON, pivote, entrada/salida).
