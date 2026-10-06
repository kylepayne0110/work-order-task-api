from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import (
    create_database_tables,
    get_database_session,
    test_database_connection,
)
from app.models import WorkOrder
from app.schemas import WorkOrderCreate, WorkOrderResponse

app = FastAPI(title="Work Order Task API")


@app.on_event("startup")
def on_startup():
    create_database_tables()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def database_check():
    result = test_database_connection()
    return {"database": "connected", "test_result": result}


@app.post("/work-orders", response_model=WorkOrderResponse)
def create_work_order(
    work_order: WorkOrderCreate,
    database: Session = Depends(get_database_session),
):
    new_work_order = WorkOrder(
        title=work_order.title,
        description=work_order.description,
        status=work_order.status,
        priority=work_order.priority,
    )

    database.add(new_work_order)
    database.commit()
    database.refresh(new_work_order)

    return new_work_order


@app.get("/work-orders", response_model=list[WorkOrderResponse])
def list_work_orders(database: Session = Depends(get_database_session)):
    return database.query(WorkOrder).all()