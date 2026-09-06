from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID
from work_orchestration.application.commands.create_work import CreateWorkCommand, CreateWorkHandler
from work_orchestration.application.queries.get_work import GetWorkQuery, GetWorkHandler
from work_orchestration.infrastructure.database import SqlAlchemyWorkRepository, init_db
from work_orchestration.infrastructure.events import RabbitEventPublisher

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="HDA Work Orchestration POC", lifespan=lifespan)

class CreateWorkBody(BaseModel):
    category: str
    urgency: str
    city: str
    zone: str

@app.post("/works", status_code=201)
def create_work(body: CreateWorkBody):
    work = CreateWorkHandler(SqlAlchemyWorkRepository(), RabbitEventPublisher()).handle(
        CreateWorkCommand(**body.model_dump()))
    return {"id": str(work.id), "status": work.status.value}

@app.get("/works/{work_id}")
def get_work(work_id: UUID):
    work = GetWorkHandler(SqlAlchemyWorkRepository()).handle(GetWorkQuery(work_id))
    if not work: raise HTTPException(404, "Work not found")
    return {"id": str(work.id), "category": work.category, "urgency": work.urgency,
            "city": work.location.city, "zone": work.location.zone, "status": work.status.value}
