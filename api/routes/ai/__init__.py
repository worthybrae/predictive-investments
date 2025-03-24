# api/routes/ai/__init__.py
from fastapi import APIRouter
from api.routes.ai.prediction import router as prediction_router
from api.routes.ai.market import router as market_router
from api.routes.ai.strategy import router as strategy_router
from api.routes.ai.screening import router as screening_router

router = APIRouter(prefix="/ai", tags=["ai"])
router.include_router(prediction_router)
router.include_router(market_router)
router.include_router(strategy_router)
router.include_router(screening_router)