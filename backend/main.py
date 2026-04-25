from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analytics import router as analytics_router
from api.calendar import router as calendar_router
from api.campaigns import router as campaigns_router
from api.email_service import router as email_router
from api.generate import router as generate_router
from api.posts import router as posts_router
from api.socials import router as socials_router
from database.db import init_db


app = FastAPI(title="Bith.ai Marketing Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root():
    """Browser hits `/` by default; this avoids 404 and points you to the API surface."""
    return {
        "service": "Bith.ai Marketing Agent API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(campaigns_router)
app.include_router(calendar_router)
app.include_router(posts_router)
app.include_router(generate_router)
app.include_router(analytics_router)
app.include_router(email_router)
app.include_router(socials_router)
