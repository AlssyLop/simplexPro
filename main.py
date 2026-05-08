from algoritmoPL import metodoGrafico, metodoSimplex
from controlador import validar_grafico, validar_simplex
import fastapi

app = fastapi.FastAPI()

@app.post("/grafico")
async def grafico(problemaPL: dict):
    validar_grafico(problemaPL)
    return metodoGrafico(problemaPL)

@app.post("/simplex")
async def simplex(problemaPL: dict):
    validar_simplex(problemaPL)
    return metodoSimplex(problemaPL)