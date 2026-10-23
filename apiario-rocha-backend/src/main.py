from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from src.config.database import database
from src.config.settings import get_settings
from src.routes.administradores import router as administradores_router
from src.routes.auth import router as auth_router
from src.routes.clientes import router as clientes_router
from src.routes.colmeias import router as colmeias_router
from src.routes.empresa import router as empresa_router
from src.routes.estoque import router as estoque_router
from src.routes.financeiro import router as financeiro_router
from src.routes.fornecedores import router as fornecedores_router
from src.routes.funcionarios import router as funcionarios_router
from src.routes.lotes import router as lotes_router
from src.routes.produtos import router as produtos_router
from src.routes.rastreabilidade import router as rastreabilidade_router
from src.routes.telemetria import router as telemetria_router
from src.routes.usuarios import router as usuarios_router
from src.services.sqlite_seed import seed_sample_data

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.initialize()
    print(f"SQLite conectado: {database.path}")
    await seed_sample_data()
    yield


app = FastAPI(
    title=settings.app_name,
    description=f"API para gestão operacional, rastreabilidade e finanças da empresa {settings.company_name}.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/static/styles.css", include_in_schema=False)
async def serve_stylesheet():
    return FileResponse(BASE_DIR / "styles.css", media_type="text/css")


@app.get("/static/script.js", include_in_schema=False)
async def serve_script():
    return FileResponse(BASE_DIR / "script.js", media_type="text/javascript")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(_, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


app.include_router(auth_router)
app.include_router(empresa_router)
app.include_router(usuarios_router)
app.include_router(administradores_router)
app.include_router(funcionarios_router)
app.include_router(clientes_router)
app.include_router(fornecedores_router)
app.include_router(telemetria_router)
app.include_router(rastreabilidade_router)
app.include_router(colmeias_router)
app.include_router(lotes_router)
app.include_router(financeiro_router)
app.include_router(estoque_router)
app.include_router(produtos_router)
