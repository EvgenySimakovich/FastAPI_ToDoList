from typing import List
from fastapi import APIRouter, Depends, Response, status

from ..models.tasks import Task, TaskCreate, TaskUpdate, TaskAction
from ..services.tasks import TaskService
from ..services.auth import User, get_current_user

router = APIRouter(
    prefix='/tasks',
)


@router.get('/', response_model=List[Task])
def get_tasks(
        user: User = Depends(get_current_user),
        service: TaskService = Depends()

):
    return service.get_list(user_id=user.id)


@router.get('/{task_id}', response_model=Task)
def get_task(
        task_id: int,
        user: User = Depends(get_current_user),
        service: TaskService = Depends()
):
    return service.get(user_id=user.id, task_id=task_id)


@router.post('/', response_model=Task)
def create_tasks(task_data: TaskCreate,
                 user: User = Depends(get_current_user),
                 service: TaskService = Depends()):
    return service.create(user_id=user.id, task_data=task_data)


@router.put('/{task_id}', response_model=Task)
def update_task(
        task_id: int,
        task_data: TaskUpdate,
        user: User = Depends(get_current_user),
        service: TaskService = Depends()
):
    return service.update(user_id=user.id, task_id=task_id, task_data=task_data)


@router.put('/{task_id}/action', response_model=Task)
def complete_task(
        task_id: int,
        action: TaskAction,
        user: User = Depends(get_current_user),
        service: TaskService = Depends()
):
    return service.update_completed(user_id=user.id, task_id=task_id, action=action)


@router.delete('/{task_id}')
def delete_task(
        task_id: int,
        user: User = Depends(get_current_user),
        service: TaskService = Depends()
):
    service.delete(user_id=user.id, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)