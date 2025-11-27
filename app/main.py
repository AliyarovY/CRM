from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api.v1.endpoints import (
    auth_router,
    organizations_router,
    contacts_router,
    deals_router,
    tasks_router,
    activities_router,
    analytics_router,
)
from app.core.exceptions import (
    NotFound,
    Unauthorized,
    Forbidden,
    BadRequest,
    Conflict,
    InternalServerError,
)

app = FastAPI(
    title="CRM API",
    description="Полнофункциональное API для управления отношениями с клиентами (CRM). Включает управление контактами, сделками, задачами и аналитику.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Аутентификация и авторизация пользователей"
        },
        {
            "name": "organizations",
            "description": "Управление организациями"
        },
        {
            "name": "contacts",
            "description": "Управление контактами (CRM контакты)"
        },
        {
            "name": "deals",
            "description": "Управление сделками с различными статусами"
        },
        {
            "name": "tasks",
            "description": "Управление задачами и их статусами"
        },
        {
            "name": "activities",
            "description": "Логирование активностей (звонки, письма, встречи, заметки)"
        },
        {
            "name": "analytics",
            "description": "Аналитика и отчеты по сделкам, задачам и активностям"
        }
    ]
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFound)
async def not_found_handler(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Unauthorized)
async def unauthorized_handler(request: Request, exc: Unauthorized):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Forbidden)
async def forbidden_handler(request: Request, exc: Forbidden):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(BadRequest)
async def bad_request_handler(request: Request, exc: BadRequest):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Conflict)
async def conflict_handler(request: Request, exc: Conflict):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(InternalServerError)
async def internal_server_error_handler(request: Request, exc: InternalServerError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc.detail)},
    )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
app.include_router(contacts_router, prefix="/api/v1")
app.include_router(deals_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(activities_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "CRM API"
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    return {
        "ready": True,
        "service": "CRM API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
