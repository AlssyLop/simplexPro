# SimplexPro

**SimplexPro** es un servicio web con API REST desarrollado en Python, especializado en la resolución de problemas de **Programación Lineal** mediante el **Método Gráfico** (2 variables) y el **Método Simplex/Gran M** (N variables).

---

## Características

- **API REST con FastAPI**: Endpoints CRUD para problemas de programación lineal + resolución unificada.
- **Método Gráfico**: Encuentra vértices de la región factible, incluye restricciones de no-negatividad (`x ≥ 0`, `y ≥ 0`), gráfico matplotlib en base64 y exportación a PDF.
- **Método Simplex / Gran M**: Soporta maximización/minimización, restricciones `<=`, `>=`, `=`, variables artificiales con penalización Big-M, y retorna todas las iteraciones (tabla, pivote, entrada/salida).
- **Persistencia**: SQLite asíncrona (`aiosqlite`).
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

## Endpoints de Problemas (`/problema`)

### 1. Listar Problemas
- **Ruta**: `GET /problema/listar`
- **Query Params**: `page` (opcional, default: 1).
- **Descripción**: Obtiene una lista paginada de los problemas registrados.
- **Respuesta (200 OK)**: Lista de `ResumenProblema`.
  ```json
  [
    {
      "id": "uuid",
      "titulo": "Nombre del problema",
      "descripcion": "Opcional",
      "tipoOptimizacion": "max/min",
      "fechaCreacion": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

### 2. Obtener Solución Gráfica
- **Ruta**: `GET /problema/solucion/grafica/{id}`
- **Descripción**: Recupera los detalles y la solución de un problema resuelto por el método gráfico.
- **Respuesta (200 OK)**: `MostrarResultadoGrafico`.
  - Incluye variables, restricciones (como inecuaciones), valores de la FO y el gráfico en base64.
- **Errores**: 404 si el problema no existe.

### 3. Obtener Solución Simplex
- **Ruta**: `GET /problema/solucion/simplex/{id}`
- **Descripción**: Recupera los detalles y la solución paso a paso de un problema resuelto por el método simplex.
- **Respuesta (200 OK)**: `MostrarResultadoSimplex`.
  - Incluye variables, restricciones, valor final de la FO y la lista de iteraciones (tablas simplex).
- **Errores**: 404 si el problema no existe.

### 4. Registrar Problema
- **Ruta**: `POST /problema/registrar`
- **Query Params**: `metodo` (obligatorio: "grafico" o "simplex").
- **Cuerpo (JSON)**:
  - Para `grafico`: Requiere `x`, `y` en variables, restricciones y FO.
  - Para `simplex`: Requiere variables tipo `x1`, `x2`, ..., `xn`.
- **Flujo**:
  1. Valida la estructura según el método.
  2. Ejecuta el servicio correspondiente (`metodoGrafico` o `metodoSimplex`).
  3. Persiste el problema y el resultado en la base de datos.
- **Respuesta (201 Created)**: `{"mensaje": "Problema guardado"}`.

### 5. Actualizar Problema
- **Ruta**: `PUT /problema/actualizar`
- **Query Params**: `metodo` ("grafico" o "simplex").
- **Cuerpo (JSON)**: Similar al registro, pero debe incluir `problemaID` o `id`.
- **Respuesta (200 OK)**: `{"mensaje": "Problema actualizado"}`.

### 6. Eliminar Problema
- **Ruta**: `DELETE /problema/eliminar/{id}`
- **Respuesta (200 OK)**: `{"mensaje": "Problema eliminado"}`.
- **Errores**: 404 si no existe.

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

## Endpoints de Utilidad

### 1. Exportar a PDF
- **Ruta**: `GET /problemas/{id}/exportar`
- **Descripción**: Genera y descarga un reporte PDF del problema (actualmente enfocado en el método gráfico).
- **Respuesta (200 OK)**: Archivo binario `application/pdf`.

---

## Validaciones y Errores Comunes
- **400 Bad Request**: 
  - Falta de campos obligatorios (`titulo`, `variables`, `restricciones`, `funcion_objetivo`).
  - Formato incorrecto de variables (ej. para simplex deben ser `x1, x2...`).
  - Signos inválidos (Grafico: `<=, >=`; Simplex: `<=, >=, =`).
  - Tipo de optimización no es `max` o `min`.
- **422 Unprocessable Entity**: Error automático de FastAPI cuando el JSON no cumple con el esquema Pydantic.
- **404 Not Found**: ID de problema no existe en la base de datos.

---

## Esquema de la Base de Datos

- `problemaPL` — Problemas registrados (UUID, título, FO, tipo optimización).
- `variables` — Variables asociadas a cada problema.
- `restricciones` — Restricciones con inecuación y glosa.
- `metodoGrafico` — Resultados gráficos (vértices, mensaje, gráfico PNG en BLOB).
- `metodoSimple` — Resultados simplex (valor FO, mensaje).
- `iteracionSimple` — Cada iteración del simplex (tabla JSON, pivote, entrada/salida).
