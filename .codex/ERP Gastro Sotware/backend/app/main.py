from fastapi import FastAPI

from app.api.integrations import router as integrations_router
from app.api.workflow import router as workflow_router
from app.integrations.startup import get_health_snapshot
from app.lifespan import app_lifespan
from app.observability.metrics import configure_metrics

app = FastAPI(title="Gastro ERP Backend", version="0.1.0", lifespan=app_lifespan)
app.include_router(integrations_router)
app.include_router(workflow_router)
configure_metrics(app)


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, object]:
    return {"status": "ok", **get_health_snapshot()}
