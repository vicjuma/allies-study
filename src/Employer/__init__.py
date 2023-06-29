from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv
from typing import Optional
from src.Employer.utils import StudentHandler, TokenHandler
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer
from src.models.models import Student, Tutor, Tasks
from fastapi_restful.api_model import APIMessage
import uuid
from src.Auth import PasswordHandler, manager, load_user
from src.Worker import tutor_manager, load_user as load_tutor
from fastapi import (
        Depends,
        status,
        HTTPException,
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
                try:
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
                except:
                    return APIMessage(
                           detail="Password email not sent",
                           status_code=status.HTTP_400_BAD_REQUEST
                        )
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

    @students_endpoint.patch("/student")
    async def patchEmployer(self, payload: Request):
        return self.student_handler.patchStudent(await payload.json())

    
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
    def studentAsksQuestion(self, request: Request, _=Depends(manager)):
        return templates.TemplateResponse('student_ask_question.html', {"request": request})
    
    @students_endpoint.get("/account/student/my/questions", status_code=status.HTTP_200_OK)
    def studentChecksQuestions(self, request: Request, user=Depends(manager)):
        if user:
            tasks = session.query(Tasks).filter(Tasks.creator_id==user["id"])
            for task in tasks:
                print(task)
        return templates.TemplateResponse('student_questions.html', {"request": request, "tasks": tasks})
    
    @students_endpoint.get("/account/student/balance", status_code=status.HTTP_200_OK)
    def studentCheckBalance(self, request: Request, _=Depends(manager)):
        return templates.TemplateResponse('student_account_balance.html', {"request": request})
    
    @students_endpoint.get("/account/support", status_code=status.HTTP_200_OK)
    def getSupport(self, request: Request, _=Depends(manager)):
        return templates.TemplateResponse('support.html', {"request": request})
    
    @students_endpoint.get("/account/student/profile", status_code=status.HTTP_200_OK)
    def getProfile(self, request: Request, _=Depends(manager)):
        return templates.TemplateResponse('student_profile.html', {"request": request})
    
 
