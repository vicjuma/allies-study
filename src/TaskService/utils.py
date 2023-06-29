from src.models.models import (
    Tasks,
    TaskAttachment,
    Solution,
    SolutionAttachment,
    Bidders
)
from src.utils import DatabaseTableMixin
from src.invoiceService.utils import InvoiceHandler
from starlette.status import HTTP_404_NOT_FOUND
from fastapi import HTTPException
from fastapi_restful.api_model import APIMessage
import uuid
import json
from typing import (
    Dict,
    Any
)
from fastapi import (
    status
)
import datetime
import sqlalchemy
import shutil
import os

class TaskHandler:
    def __init__(self):
        self.task_handler = DatabaseTableMixin(Tasks)
        self.task_attachment_handler = DatabaseTableMixin(TaskAttachment)
        self.solution_handler = DatabaseTableMixin(Solution)
        self.solution_attachment_handler = DatabaseTableMixin(SolutionAttachment)
        self.invoice_handler = InvoiceHandler()
        self.bidders_handler = DatabaseTableMixin(Bidders)

    def getTask(self, task_id):
        if self.task_handler[task_id]:
            return self.task_handler[task_id].to_json()
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    def getTasks(self):
        return {
                "tasks": [
                    item.to_json() for item in self.task_handler    
                ]
            }

    def createTask(self, payload: Dict[str, Any], user):
        # Check for Authentication token in headers        
        # task id
        # payload["id"] = uuid.uuid4().hex
        
         # task = Tasks(
            #     content=content_data, 
            #     topics=subject, 
            #     timeline=timeline, 
            #     amount=amount, 
            #     notification=is_checked, 
            #     creator_id=user["id"], 
            #     subject_id=subject_is)
            #   static_dir = os.path.join(f"{os.getcwd()}/src", "static/siteImages")
            #     destination = os.path.join(static_dir, file.filename)
            #     print(static_dir)
            #     print(destination)
            #     with open(f"{destination}", "wb") as f:
            #         shutil.copyfileobj(file.file, f)
            # print(payload)
        payload["creator_id"] = user['id']
        payload['task_deadline'] = datetime.datetime.utcnow() + datetime.timedelta(days=10) 
        
        self.task_handler.__create_item__(payload)
        
        # post to invoices
        self.invoice_handler.createInvoice({
                "task_id": payload['id'],
                "amount": payload['Amount']
            },
            user
        )
        return self.task_handler[payload['id']].to_json()

    def updateTask(self, payload: Dict[str, Any], user: Dict[str, Any]):
        task_id = payload['id']
        task = self.task_handler[task_id]

        if task:
            # Check if user id is task Creator
            if user["id"] == task.creator_id or user['is_admin'] == True:
                task = payload
                return self.task_handler[task_id].to_json()
            raise HTTPException(
                        detail="Unauthorized access",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    def deleteTask(self, task_id, user):
        task = self.task_handler[task_id]

        if task:
            # Check if user is_administrator
            if task["creator_id"] == user['id'] or user["is_admin"] == True:
                del task
                return APIMessage(
                        detail="Task deletion success",
                        status_code=status.HTTP_200_OK
                    )
            raise HTTPException(
                    detail="Unauthorized access",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        else:
            # Raise 404, error
            raise HTTPException(
                    detail="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
    
    def addAtachment(self, file, payload: Dict[str, Any], user: Dict[str, Any]):
        # Check if the task exists
        task = self.task_handler[payload['task_id']]
        if task:
            # ensure that user uploading the file is the owner of the file or the administrator
            if user['id'] == task.creator_id or user['is_admin'] == True:

                dst_folder = os.path.join(os.getcwd(), "/attachment/assignment")

                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)

                dst = os.path.join(dst_folder, file.filename)
                
                with open(dst, "wb") as buf:
                    shutil.copyfileobj(file.file, buf)
                # Create Attachment
                res_ = {
                        # "id": uuid.uuid4().hex,
                        "task_id": task.id,
                        "attachment_name": file.filename 
                    }
                self.task_attachment_handler.__create_item(**res_)
                return res_ 
            raise HTTPException(
                    detail="Unauthorized Access",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        raise HTTPException(
                detail="task does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def bidTask(self, task_id: str, user: Dict[str, Any]):
        if self.task_handler[task_id]:

            # Create Bidders to task item

            return self.task_handler[task_id].to_json()
        raise HTTPException(
                    detail="Task does not exist",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def claimTask(self, payload: Dict[str, Any], user:Dict[str, Any]) -> Dict[str, Any]:
        # Get the Task
        task = self.task_handler[payload['id']]

        if task:
            # update the Progress status of task from unclaimed to claimed and task_creator to 
            # Current user
            update_payload = {
                        "progress_status": "claimed",
                        "tutor_id": payload["tutor_id"]
                    }
            self.task_handler.patchDb(update_payload)

            return APIMessage(
                    detail=f"Task successfully assigned to {user['name']}",
                    status_code=status.HTTP_201_CREATED
                )
        raise HTTPException(
                detail="Task not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def submitAnswer(self, payload: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        # get the task
        task = self.task_handler[payload['task_id']]

        if task:
            # Check if the assigned user is the one submitting the file
            if task.tutor_id == user['id']:
                # create Solution
                # payload['id'] = uuid.uuid4().hex
                self.solution_handler.__create_item__(**payload)
                return payload
            raise HTTPException(
                    detail="Unauthorized access",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        raise HTTPException(
                detail="Task not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def addAnswerAttachment(self, file, payload: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        # Find the solution
        solution = self.solution_handler[payload['solution_id']]
        if solution:
            # Check if the authenticated user was assigned the file
            if solution.tutor_id == user['id']:
                # Save the File to path
                dst_folder = os.path.join(os.getcwd(), "/attachment/solutions")

                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)

                dst = os.path.join(dst_folder, file.filename)
                
                with open(dst, "wb") as buf:
                    shutil.copyfileobj(file.file, buf)

                # payload['id'] = uuid.uuid4().hex
                payload['file_name'] = file.filename
                self.solution_attachment_handler.__create_item__(**payload)
                return payload
            raise HTTPException(
                    detail="Authorization failure",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        raise HTTPException(
                detail="Solution not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def getUserTasks(self, user: Dict[str, Any]) -> Dict[str, Any]:
        return self.task_handler.filterDb(task_id=user['id']).first().to_json()


