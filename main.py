from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.connection import init_db
from app.routes import resolver, problemas, utilidad

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar base de datos si no existe
    await init_db()
    yield

app = FastAPI(title="SimplexPro API", lifespan=lifespan)

# Registrar routers
app.include_router(resolver.router)
app.include_router(problemas.router)
app.include_router(utilidad.router)
