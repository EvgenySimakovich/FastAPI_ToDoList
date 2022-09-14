from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from .. import tables
from ..models import tasks
from ..database import get_session


class TaskService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, user_id: int, task_id: int) -> tables.Task:
        task = (
            self.session
            .query(tables.Task)
            .filter_by(
                id=task_id,
                user_id=user_id)
            .first()
        )
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Task not found')
        return task

    def get_list(self, user_id: int) -> List[tables.Task]:
        tasks = (
            self.session
            .query(tables.Task)
            .filter_by(user_id=user_id)
            .all()
        )
        return tasks

    def get(self, user_id: int, task_id: int) -> tables.Task:
        return self._get(user_id=user_id, task_id=task_id)

    def create(self, user_id: int, task_data: tasks.TaskCreate) -> tables.Task:
        task = tables.Task(
            **task_data.dict(),
            user_id=user_id
        )
        self.session.add(task)
        self.session.commit()
        return task

    def update(self, user_id: int, task_id: int, task_data: tasks.TaskUpdate) -> tables.Task:
        task = self._get(user_id=user_id, task_id=task_id)
        for field, value in task_data:
            setattr(task, field, value)
        self.session.commit()
        return task

    def update_completed(self, user_id: int, task_id: int, action: tasks.TaskAction) -> tables.Task:
        task = self._get(user_id=user_id, task_id=task_id)
        if action == 'open':
            task.is_complete = False
        if action == 'close':
            task.is_complete = True
        self.session.commit()
        return task

    def delete(self, user_id: int, task_id: int) -> None:
        task = self._get(user_id=user_id, task_id=task_id)
        self.session.delete(task)
        self.session.commit()

