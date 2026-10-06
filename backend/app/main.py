from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    create_database_tables,
    get_database_session,
    test_database_connection,
)
from app.models import WorkOrder, WorkOrderTask
from app.schemas import (
    WorkOrderCreate,
    WorkOrderResponse,
    WorkOrderTaskCreate,
    WorkOrderTaskResponse,
    WorkOrderTaskUpdate,
    WorkOrderUpdate,
)

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Work Order Task API")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.on_event("startup")
def on_startup():
    create_database_tables()

@app.get("/")
def read_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")

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

@app.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: int,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    return work_order


@app.patch("/work-orders/{work_order_id}/complete", response_model=WorkOrderResponse)
def complete_work_order(
    work_order_id: int,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    work_order.is_complete = True
    work_order.status = "complete"

    database.commit()
    database.refresh(work_order)

    return work_order

@app.delete("/work-orders/{work_order_id}")
def delete_work_order(
    work_order_id: int,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    database.delete(work_order)
    database.commit()

    return {"message": "Work order deleted"}

@app.put("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: int,
    updated_work_order: WorkOrderUpdate,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    work_order.title = updated_work_order.title
    work_order.description = updated_work_order.description
    work_order.status = updated_work_order.status
    work_order.priority = updated_work_order.priority
    work_order.is_complete = updated_work_order.is_complete

    database.commit()
    database.refresh(work_order)

    return work_order


@app.post(
    "/work-orders/{work_order_id}/tasks",
    response_model=WorkOrderTaskResponse,
)
def create_work_order_task(
    work_order_id: int,
    task: WorkOrderTaskCreate,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    new_task = WorkOrderTask(
        work_order_id=work_order_id,
        title=task.title,
        description=task.description,
    )

    database.add(new_task)
    database.commit()
    database.refresh(new_task)

    return new_task

@app.get(
    "/work-orders/{work_order_id}/tasks",
    response_model=list[WorkOrderTaskResponse],
)
def list_work_order_tasks(
    work_order_id: int,
    database: Session = Depends(get_database_session),
):
    work_order = (
        database.query(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .first()
    )

    if work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    return (
        database.query(WorkOrderTask)
        .filter(WorkOrderTask.work_order_id == work_order_id)
        .all()
    )

@app.patch("/tasks/{task_id}/complete", response_model=WorkOrderTaskResponse)
def complete_work_order_task(
    task_id: int,
    database: Session = Depends(get_database_session),
):
    task = (
        database.query(WorkOrderTask)
        .filter(WorkOrderTask.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_complete = True

    database.commit()
    database.refresh(task)

    return task

@app.delete("/tasks/{task_id}")
def delete_work_order_task(
    task_id: int,
    database: Session = Depends(get_database_session),
):
    task = (
        database.query(WorkOrderTask)
        .filter(WorkOrderTask.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    database.delete(task)
    database.commit()

    return {"message": "Task deleted"}

@app.put("/tasks/{task_id}", response_model=WorkOrderTaskResponse)
def update_work_order_task(
    task_id: int,
    updated_task: WorkOrderTaskUpdate,
    database: Session = Depends(get_database_session),
):
    task = (
        database.query(WorkOrderTask)
        .filter(WorkOrderTask.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.is_complete = updated_task.is_complete

    database.commit()
    database.refresh(task)

    return task