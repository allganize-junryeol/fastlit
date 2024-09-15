from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.events.views import router as event_router
from backend.statistics.views import router as statistics_router
from backend.ssh.views import router as ssh_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=event_router, tags=["ip"])
app.include_router(router=statistics_router, tags=["link"])
app.include_router(router=ssh_router, tags=["ssh"])

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")

@app.get("/health")
async def health():
    return {"message": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    