from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv
from typing import Optional
import os
import asyncio
import shutil
from src.Employer.utils import StudentHandler, TokenHandler
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer
from src.models.models import Student, Tutor, Tasks, TaskAttachment, StudentBalances
from fastapi_restful.api_model import APIMessage
import uuid
from src.Auth import PasswordHandler, manager, load_user
from src.Worker import tutor_manager, load_user as load_tutor
from fastapi import (
        Depends,
        status,
        HTTPException,
        UploadFile,
        File
    )
from fastapi.responses import RedirectResponse
from src.utils import (
        decode_access_token,
        get_templates,
        generate_password,
        generate_password_hash,
        DatabaseStudentTableMixin,
        DatabaseTableMixin
    )

from src.models.schema import(
        LoginSchema,
        StudentSchema,
        StudentsSchema,
        DeletionSchema,
        ResetPasswordSchema,
    )
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from intasend import APIService

token = "ISSecretKey_live_683434d0-e26c-4938-8de5-5c03d056e3ad"
publishable_key = "ISPubKey_live_f1ec1f68-2f77-4cba-a44f-28ca77e4afce"
service = APIService(token="token",publishable_key=publishable_key)

DB_NAME="studyallies"
DB_PASSWD="studyuserpassword"
DB_AUTHOR="study_user"

databasefilename: str = f'mysql+pymysql://{DB_AUTHOR}:{DB_PASSWD}@localhost/{DB_NAME}'
engine = create_engine(databasefilename)
Session = sessionmaker(bind=engine, expire_on_commit=False)

session = Session()

students_endpoint = InferringRouter()


token_path = OAuth2PasswordBearer(
        tokenUrl="/students/login",
        scheme_name="JWT"
    )

templates = get_templates()

@cbv(students_endpoint)
class StudentsRouter:
    def __init__(self):
        self.student_handler = StudentHandler()
        self.token_handler = TokenHandler()
        self.employerHandler = DatabaseStudentTableMixin(Student)
        self.TutorHandler = DatabaseStudentTableMixin(Tutor)
        self.password_handler = PasswordHandler()
        self.task_handler = DatabaseTableMixin(Tasks)
    
    @students_endpoint.get("/student", status_code=status.HTTP_200_OK, response_model=StudentsSchema)
    def getEmployers(self):
        return self.student_handler.getStudents()
    
    @students_endpoint.get("/", status_code=status.HTTP_200_OK)
    def home(self, request: Request, user=Depends(manager.optional)):
        return templates.TemplateResponse('index.html', {"request": request, "user": user})
    
    @students_endpoint.get("/auth/login", status_code=status.HTTP_200_OK)
    def authLogin(self, request: Request, user=Depends(manager.optional)):
        return templates.TemplateResponse('auth_login.html', {"request": request, "user": user})
    
    @students_endpoint.post("/", status_code=status.HTTP_200_OK)
    async def post_home(self, request: Request, payload: LoginSchema):
        return self.student_handler.loginStudent(payload.dict())


    @students_endpoint.get("/student/{student_email}", status_code=status.HTTP_200_OK)
    def getEmployerByID(self, student_email: str) -> Optional[StudentSchema]:
        data = self.student_handler.getStudent(student_email)
        if data:
            return data
        else:
            # response_data = {
            #     "message": "User not found",
            #     "status_code": 404
            # }
            return None
    
    @students_endpoint.post("/student/create", status_code=status.HTTP_201_CREATED)
    async def createEmployer(self, request: Request):
        form_data = await request.form()
        payload = dict(form_data)
        username = form_data.get("username")
        email = form_data.get("email")
        user_email = self.employerHandler.filterDb(email=email).first()
        user_name = self.employerHandler.filterDb(username=username).first()
        print(payload)
        
        if user_name and user_email:
            message = "Username and Email already exist in our database"
            return templates.TemplateResponse('success/email_and_username_exist.html', {"request": request, "message": message})
        elif user_name:
            message = "Username already exists in our database"
            return templates.TemplateResponse('success/username_exists.html', {"request": request, "message": message})
        elif user_email:
            message = "Email already exists in our database"
            return templates.TemplateResponse('success/email_exists.html', {"request": request, "message": message})
        else:
            # Genereate user id
            # payload['id'] = uuid.uuid4().hex
            password = generate_password()
            payload['password'] = generate_password_hash(password)
            # Save to db
            payload['department'] = "student"
            self.employerHandler.__create_item__(payload)

            # Send mail to Student to Set his password
            user = self.employerHandler.filterDb(email=payload['email']).first()
            if user:
                # try:
                    created_user_id = self.employerHandler.filterDb(email=payload["email"]).first().to_json()["id"]
                    payload["id"] = created_user_id
                    payload['password'] = password
                    self.password_handler.set_password(payload)
                    message = "Email sent successfully with your password, check your inbox or spam"
                    return templates.TemplateResponse('success/email_sent.html', {"request": request, "message": message})
                    # return APIMessage(
                    #     detail="Password set email successfully sent",
                    #     status_code=status.HTTP_200_OK
                    # )
                # except:
                #     return APIMessage(
                #            detail="Password email not sent",
                #            status_code=status.HTTP_400_BAD_REQUEST
                #         )
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            # return self.setPassword(payload)
    
    @students_endpoint.post("/student/set/password")
    async def verifyAccount(self, request: Request, payload: ResetPasswordSchema):
        return self.student_handler.updatePassword(payload.dict())
    
    @students_endpoint.post("/reset/password")
    async def resetPassword(self, request: Request, payload: ResetPasswordSchema):
        return self.student_handler.resetPassword(
                    payload.dict()
                )

    @students_endpoint.delete("/student", status_code=status.HTTP_200_OK, response_model=DeletionSchema)
    async def deleteEmployer(self, payload: Request):
        return self.student_handler.deleteStudent(await payload.json()['id'])

    @students_endpoint.put("/student")
    async def updateEmployer(self, payload: StudentSchema, request: Request):
        return self.student_handler.updateStudent(payload.dict())

    @students_endpoint.post("/account/student/profile/{username}")
    async def patchEmployer(self, request: Request, username: str, file: UploadFile = File(...), _=Depends(manager)):
        student = session.query(Student).filter(Student.username==username).first()
        if not student:
            raise HTTPException(status_code=404, detail="User not found")
        form_data = await request.form()
        # payload = dict(form_data)
        student.username = form_data.get("username")
        student.email = form_data.get("email")
        student.password = generate_password_hash(form_data.get("password"))
        student.profile_pic = file.filename
        static_dir = os.path.join(f"{os.getcwd()}/src", "static/profileImages")
        destination = os.path.join(static_dir, file.filename)
        with open(f"{destination}", "wb") as f:
            shutil.copyfileobj(file.file, f)
        session.commit()
        return {"message": "User updated successfully"}

    
    @students_endpoint.get("/account/user/verify/{token}", status_code=status.HTTP_200_OK)
    def verify_me(self, token: str):
        decoded_token = decode_access_token(token)
        print(decoded_token)
        student_data = self.token_handler.getStudent(decoded_token)
        tutor_data = self.token_handler.getTutor(decoded_token)
        user = student_data if student_data else tutor_data
        print(student_data)
        print(tutor_data)
        if not user:
            return RedirectResponse("/permission/denied", status_code=status.HTTP_403_FORBIDDEN)
        else:
            if user["department"] == "student":
                access_token = manager.create_access_token(
                        data={"sub":student_data["username"]}
                    )
                load_user(user["username"])
                resp = RedirectResponse("/account/student/ask/question", status_code=status.HTTP_302_FOUND)
                manager.set_cookie(resp, access_token)
                return resp
        access_token = manager.create_access_token(
                data={"sub":user["username"]}
            )
        load_tutor(user["username"])
        resp = RedirectResponse("/account/tutor/my/answers", status_code=status.HTTP_302_FOUND)
        tutor_manager.set_cookie(resp, access_token)
        return resp
    
    @students_endpoint.get("/account/student/ask/question", status_code=status.HTTP_200_OK)
    def studentAsksQuestion(self, request: Request, user=Depends(manager)):
        student = session.query(Student).filter(Student.username==user["username"]).first()
        return templates.TemplateResponse('student_ask_question.html', {"request": request, "student": student})
    
    @students_endpoint.get("/account/student/my/questions", status_code=status.HTTP_200_OK)
    def studentChecksQuestions(self, request: Request, user=Depends(manager)):
        student = session.query(Student).filter(Student.username==user["username"]).first()
        if user:
            tasks = session.query(Tasks).filter(Tasks.creator_id==user["id"])
            for task in tasks:
                print(task)
        return templates.TemplateResponse('student_questions.html', {"request": request, "tasks": tasks, "student": student})
    
    @students_endpoint.get("/account/student/my/questions/{task_id}", status_code=status.HTTP_200_OK)
    def studentCheckSingleQuestion(self, request: Request, task_id: int, user=Depends(manager)):
        student = session.query(Student).filter(Student.username==user["username"]).first()
        task = session.query(Tasks).filter(Tasks.id==task_id).first()
        images = session.query(TaskAttachment).filter(task_id==task_id)
        return templates.TemplateResponse('single_question_choose.html', {"request": request, "task": task, "images": images, "student": student})
    
    @students_endpoint.get("/account/student/balance", status_code=status.HTTP_200_OK)
    def studentCheckBalance(self, request: Request, user=Depends(manager)):
        student = session.query(Student).filter(Student.username==user["username"]).first()
        transactions = session.query(StudentBalances).filter(Student.id==user["id"])
        return templates.TemplateResponse('student_account_balance.html', {"request": request, "student": student, "transactions": transactions})
    
    @students_endpoint.get("/account/support", status_code=status.HTTP_200_OK)
    def getSupport(self, request: Request, user=Depends(manager)):
        student = session.query(Student).filter(Student.username==user["username"]).first()
        return templates.TemplateResponse('support.html', {"request": request, "student": student})
    
    @students_endpoint.get("/account/student/profile/{username}", status_code=status.HTTP_200_OK)
    def getProfile(self, request: Request, username: str, _=Depends(manager)):
        student = session.query(Student).filter(Student.username==username).first()
        return templates.TemplateResponse('student_profile.html', {"request": request, "student": student, "username": username})
    
    @students_endpoint.post("/account/student/load-account")
    async def loadStudentAccount(self, request: Request, user=Depends(manager)):
        student = session.query(Student).filter(Student.id==user["id"]).first()
        form_data = await request.form()
        payload = dict(form_data)
        amount = form_data.get("load")
        phone = "254728877619"
        
        service = APIService(token="ISSecretKey_live_683434d0-e26c-4938-8de5-5c03d056e3ad",publishable_key="ISPubKey_live_f1ec1f68-2f77-4cba-a44f-28ca77e4afce", test=False)
        initial_response = service.collect.mpesa_stk_push(
            phone_number=phone, email=user["email"], amount=amount, narrative="Fees")
        invoice_id = initial_response["invoice"]["invoice_id"]
        await asyncio.sleep(20)
        print(invoice_id)
        final_response = service.collect.status(invoice_id=invoice_id)
        
        if final_response["invoice"]["state"] == "COMPLETE":
            transaction = StudentBalances(amount=amount, student_id=user["id"], code=final_response["invoice"]["mpesa_reference"])
            session.add(transaction)
            session.commit()
        else:
            {"message": "payment could not be initialized"}
        return final_response
    
 
