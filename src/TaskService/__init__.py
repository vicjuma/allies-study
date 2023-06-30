from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv
import os
import uuid
import shutil
import datetime
from src.TaskService.utils import TaskHandler
from fastapi.responses import RedirectResponse
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
from src.utils import DatabaseTableMixin, DatabaseStudentTableMixin, get_templates, DatabaseTasksTableMixin
from src.models.models import (
    Tasks,
    TaskAttachment,
    Subject,
    Student
)
from src.Auth.manager import manager as AuthManager
from src.Worker import tutor_manager as TaskManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_NAME="studyallies"
DB_PASSWD="studyuserpassword"
DB_AUTHOR="study_user"


databasefilename: str = f'mysql+pymysql://{DB_AUTHOR}:{DB_PASSWD}@localhost/{DB_NAME}'
engine = create_engine(databasefilename)
Session = sessionmaker(bind=engine, expire_on_commit=False)

session = Session()

templates = get_templates()

task_endpoint = InferringRouter()

IMGDIR = 'images/'

@cbv(task_endpoint)
class TaskEndpoint:
    def __init__(self):
        self.task_handler = TaskHandler()
        self.task_item_handler = DatabaseTableMixin(Tasks)
        self.task_attachment_handler = DatabaseTableMixin(TaskAttachment)
        self.subj_handler = DatabaseStudentTableMixin(Subject)
        self.task_id_handler = DatabaseStudentTableMixin(Tasks)
    
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
        un_id = uuid.uuid4().hex
        payload_data = {
            # "id": uuid.uuid4().hex,
            "content": content_data, 
            "topics": subject,
            "timeline": timeline,
            "amount": amount,
            "notification": is_checked,
            "creator_id": user["id"],
            "subject_id": subject_is,
            "unique_id": un_id}
        payload = {**payload, **payload_data}
        self.task_item_handler.__create_item__(payload_data)
        result = session.query(Tasks).filter(Tasks.unique_id==un_id).first()
        for file in files:
            file_payload = {
                # "id": uuid.uuid4().hex,
                "task_id": result.id,
                "attachment_name": file.filename,
            }
            # new_file = File(**file_payload)
            self.task_attachment_handler.__create_item__(file_payload)
            static_dir = os.path.join(f"{os.getcwd()}/src", "static/siteImages")
            destination = os.path.join(static_dir, file.filename)
            print(static_dir)
            print(destination)
            with open(f"{destination}", "wb") as f:
                shutil.copyfileobj(file.file, f)
            print(payload)
        student = session.query(Student).filter(Student.username==user["username"]).first()
        if user:
            tasks = session.query(Tasks).filter(Tasks.creator_id==user["id"])
            for task in tasks:
                print(task)
        return templates.TemplateResponse('student_questions.html', {"request": request, "tasks": tasks, "student": student})

    @task_endpoint.get("/homework/answers", status_code=status.HTTP_200_OK)
    def getTasks(self, request: Request):
        tasks = self.task_handler.getTasks()
        return templates.TemplateResponse('homework_answers.html', {"request": request, "tasks": tasks})

    @task_endpoint.get("/task/{taskid}", status_code=status.HTTP_200_OK, response_model=TaskSchema)
    def getTask(self, taskid: str, request: Request, _=Depends(AuthManager)):
        task = self.task_handler.getTask(taskid)
        return templates.TemplateResponse('single_question_choose.html', {"request": request})

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
    
    @task_endpoint.get("/tutor/support/write")
    def requestSupport(self, request: Request):
        return templates.TemplateResponse('contact_support.html', {"request": request})
    
    @task_endpoint.post("/tutor/support/write")
    async def contactSupport(self, request: Request, user=Depends(AuthManager)):
        form_data = await request.form()
        payload = dict(form_data)
        suppoty_type = form_data.get("supportType")
        order_id = form_data.get("orderID")
        subject = form_data.get("subject")
        user_message = form_data.get("message")
        
        PORT = 465
        SENDER_MAIL = user["email"]
        MAIL_SERVER='mail.studyallies.com'
        MAIL_USERNAME = user["username"]
        MAIL_PASSWORD = "studyallies@254"
        RECEIVER_EMAIL = "support@studyallies.com"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_MAIL
        message["To"] = RECEIVER_EMAIL
        
        text = f"Name: {MAIL_USERNAME}\nEmail: {SENDER_MAIL}\n\n{user_message}"
        html = f"<p><strong>Name:</strong> {MAIL_USERNAME}</p><p><strong>Email:</strong> {SENDER_MAIL}   </p><p>{user_message}</p>"
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        with smtplib.SMTP(MAIL_SERVER, PORT) as server:
            server.starttls()
            server.login("support@studyallies.com", "studyallies@254")
            server.sendmail(SENDER_MAIL, RECEIVER_EMAIL, message.as_string())
        # return templates.TemplateResponse('contact_support.html', {"request": request})
        return {"Response": "Email sent successfully"}

