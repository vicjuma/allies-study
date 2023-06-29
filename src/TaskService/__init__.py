from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv
import uuid
import datetime
from src.TaskService.utils import TaskHandler
from fastapi import (
        Depends,
        status,
        File,
        UploadFile,
        Request
    )
from src.models.schema import (
    TaskSchema,
    TaskAttachmentSchema,
    CreateTaskAttachmentSchema,
    TaskIdSchema,
    SolutionSchema,
    CreateSolutionAttachmentSchema,
    SolutionAttachmentSchema
)
from typing import (
    List
)
from src.utils import DatabaseTableMixin, DatabaseStudentTableMixin, get_templates
from src.models.models import (
    Tasks,
    TaskAttachment,
    Subject
)
from src.Auth.manager import manager as AuthManager
from src.Worker import manager as TaskManager

templates = get_templates()

task_endpoint = InferringRouter()

@cbv(task_endpoint)
class TaskEndpoint:
    def __init__(self):
        self.task_handler = TaskHandler()
        self.task_item_handler = DatabaseTableMixin(Tasks)
        self.task_attachment_handler = DatabaseTableMixin(TaskAttachment)
        self.subj_handler = DatabaseStudentTableMixin(Subject)
    
    @task_endpoint.post("/account/student/create/tasks", status_code=status.HTTP_201_CREATED)
    async def createTask(self, request: Request, files: List[UploadFile] = File(...), user=Depends(AuthManager)):
        form_data = await request.form()
        payload = dict(form_data)
        content_data = form_data.get("content_data")
        subject = form_data.get("subject")
        timeline_html = form_data.get("timeline")
        timeline = datetime.datetime.strptime(timeline_html, "%Y-%m-%dT%H:%M")
        amount = form_data.get("amount")
        notification = form_data.get("notification")
        is_checked = True if notification == "on" else False
        subject_is = self.subj_handler.filterDb(suject_name=subject).first()
        payload_data = {
            # "id": uuid.uuid4().hex,
            "content": content_data, 
            "topics": subject,
            "timeline": timeline,
            "amount": amount,
            "notification": is_checked,
            "creator_id": user["id"],
            "subject_id": subject_is}
        payload = {**payload, **payload_data}
        print(payload)
        self.task_item_handler.__create_item__(payload_data)
        for file in files:
            file_payload = {
                # "id": uuid.uuid4().hex,
                "task_id": payload["id"],
                "attachment_name": file.filename,
            }
            # new_file = File(**file_payload)
            self.task_attachment_handler.__create_item__(file_payload)
        print(payload)
        return {"Message":"Task Created Successfully"}

    @task_endpoint.get("/homework/answers", status_code=status.HTTP_200_OK)
    def getTasks(self, request: Request):
        tasks = self.task_handler.getTasks()
        return templates.TemplateResponse('homework_answers.html', {"request": request, "tasks": tasks})

    @task_endpoint.get("/task/{taskid}", status_code=status.HTTP_200_OK, response_model=TaskSchema)
    def getTask(self, taskid: str, request: Request, _=Depends(AuthManager)):
        task = self.task_handler.getTask(taskid)
        return templates.TemplateResponse('student_ask_question.html', {"request": request})

    @task_endpoint.patch("/task", status_code=status.HTTP_200_OK, response_model=TaskSchema)
    async def updateTask(self, payload: Request):
        return self.task_handler.updateTask(await payload.json())

    @task_endpoint.delete("/task", status_code=status.HTTP_200_OK)
    async def deleteTask(self, request: Request, payload: TaskIdSchema):
        return self.task_handler.deleteTask(payload.dict()['id'])
        
    @task_endpoint.post("/add/file/task", status_code=status.HTTP_201_CREATED, response_model=TaskAttachmentSchema)
    async def addAttachemnt(self, file: UploadFile, payload: CreateTaskAttachmentSchema):
        return self.task_handler.addAttachemnt(file, payload.dict())

    @task_endpoint.get("/my/tasks")
    def getStudentTasks(self):
        return self.task_handler.getUserTask()

    # Workers can  bid for tasks
    @task_endpoint.post("/bid/task/{task_id}")
    def bidTask(self, task_id: str):
        self.task_handler.bidTask(task_id)

    @task_endpoint.post("/claim/task")
    async def claimTask(self, request: Request, payload: TaskIdSchema):
        return self.task_handler.claimTask(payload.dict())

    @task_endpoint.post("/submit/solution/task")
    async def submitSolution(self, request: Request, payload: SolutionSchema):
        return self.task_handler.submitAnswer(payload.dict())

    @task_endpoint.post("/add/solution/attachment", status_code=status.HTTP_201_CREATED, response_model=SolutionAttachmentSchema)
    async def addAttachmentSolution(self, file:UploadFile, payload: CreateSolutionAttachmentSchema):
        return self.task_handler.addAnswerAttachment(file, payload.dict())
    
    @task_endpoint.get("/tutor/available/tasks")
    def getStudentTasks(self, request: Request, _=Depends(TaskManager)):
        tasks = self.task_handler.getTasks()["tasks"]
        for task in tasks:
            print(task)
        return templates.TemplateResponse('tutor_find_questions.html', {"request": request, "tasks": tasks})

