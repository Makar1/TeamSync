from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as get_user_router
from app.api.teams import router as team_router
from app.api.tasks import tasks_router, comments_router, evaluations_router
from app.api.meetings import meetings_router
from app.api.calendar import calendar_router

def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
                  )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем роутеры
    app.include_router(auth_router)
    app.include_router(get_user_router)
    app.include_router(team_router)
    app.include_router(tasks_router)
    app.include_router(comments_router)
    app.include_router(meetings_router)
    app.include_router(evaluations_router)
    app.include_router(calendar_router)

    # Health check
    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app

app = create_app()