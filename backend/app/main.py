import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.supplier import router as supplier_router
from app.routes.product import router as product_router
from app.routes.stock import router as stock_router
from app.routes.ml_integration import router as ml_integration_router
from app.routes.ml_webhook import router as ml_webhook_router
from app.routes.product_mapping import router as product_mapping_router
from app.routes.order import router as order_router
from app.routes.dashboard import router as dashboard_router
from app.routes.admin import router as admin_router

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS")
    if not raw_origins:
        return DEFAULT_CORS_ORIGINS

    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(
    title=os.getenv("APP_NAME", "Sistema DRI"),
    root_path=os.getenv("API_ROOT_PATH", ""),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(supplier_router)
app.include_router(product_router)
app.include_router(stock_router)
app.include_router(ml_integration_router)
app.include_router(ml_webhook_router)
app.include_router(product_mapping_router)
app.include_router(order_router)
app.include_router(dashboard_router)
app.include_router(admin_router)


@app.get("/")
def home():
    app_name = os.getenv("APP_NAME", "Sistema DRI")
    return {"mensagem": f"API do {app_name} rodando"}
