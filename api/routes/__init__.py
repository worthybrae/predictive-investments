# api/routes/__init__.py
"""API routes."""
from fastapi import APIRouter
from routes.stock import router as stocks_router
from routes.options import router as options_router
from routes.indices import router as indices_router
from routes.finviz import router as finviz_router
from routes.ai import router as ai_router

router = APIRouter()
router.include_router(stocks_router)
router.include_router(options_router)
router.include_router(indices_router)
router.include_router(finviz_router)
router.include_router(ai_router)