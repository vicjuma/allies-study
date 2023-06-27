from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv
from src.Worker.utils import (
        TutorHandler,
    )
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer
from fastapi import (
        Depends,
        status,
    )

from src.models.models import Tutor, Tutorial
from src.models.schema import(
        TutorSchema,
        LoginSchema,
        TutorsSchema,
        ResetPasswordSchema
    )
from fastapi_restful.api_model import APIMessage
import uuid
from jose import jwt
from typing import (
        Dict,
        Any
    )
from src.utils import (
        ALGORITHM,
        DatabaseTableMixin,
        get_templates
    )

from src.utils import generate_password_hash, generate_password
from fastapi import (
        Depends,
        status,
        HTTPException,
    )
from src.Auth.handlers import PasswordHandler
from fastapi_login import LoginManager
# from src.Worker.utils import TutorHandler

SECRET = "studyalliessiteforstudentsandtuitors"

manager = LoginManager(SECRET, "/auth/login",use_cookie=True)
manager.cookie_name = "studyalliescookie"

@manager.user_loader()
def load_user(username:str):
    sharedInst = TutorHandler()
    user = sharedInst.getTutor(username)
    return user


templates = get_templates()

tutor_endpoint = InferringRouter()

token_path = OAuth2PasswordBearer(
        tokenUrl="/tutor/login",
        scheme_name="JWT"
    )

JWT_SECRET_KEY = "hellothere"


@cbv(tutor_endpoint)
class TutorRouter:
    def __init__(self):
        self.tutor_handle = TutorHandler()
        self.TutorHandler = DatabaseTableMixin(Tutor)
        self.tutorial_hander = DatabaseTableMixin(Tutorial)
        self.password_handler = PasswordHandler()
    
    @tutor_endpoint.get("/tutor", status_code=status.HTTP_200_OK, response_model=TutorsSchema)
    def getTutors(self):
        return self.tutor_handle.getTutors()

    @tutor_endpoint.get("/tutor/{tutorid}", status_code=status.HTTP_200_OK, response_model=TutorSchema)
    def getTutorByID(self, tutorid: int):
        return self.tutor_handle.getTutor(tutorid)
    
    @tutor_endpoint.post("/tutor/create", status_code=status.HTTP_201_CREATED)
    async def createTutor(self, request: Request):
        form_data = await request.form()
        payload = dict(form_data)
        username = form_data.get("username")
        email = form_data.get("email")
        user_email = self.TutorHandler.filterDb(email=email).first()
        user_name = self.TutorHandler.filterDb(username=username).first()
        
        if user_email:
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
        elif user_name:
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already exists"
                    )
        elif user_name and user_email:
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username and Email already exist"
                    )
        else:
            # Genereate user id
            payload['id'] = uuid.uuid4().hex
            password = generate_password()
            payload['password'] = generate_password_hash(password)
            # Save to db
            self.TutorHandler.__create_item__(payload)
            payload['password'] = password

            # Send mail to Student to Set his password
            user = self.TutorHandler.filterDb(email=payload['email']).first()
            if user:
                try:
                    self.password_handler.set_password(payload)
                    return APIMessage(
                        detail="Password set email successfully sent",
                        status_code=status.HTTP_200_OK
                    )
                except:
                    return APIMessage(
                           detail="Password email not sent",
                           status_code=status.HTTP_400_BAD_REQUEST
                        )
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        

    # ###############################################################################
    # LEFT HERE
    #################################################################################
    @tutor_endpoint.post("/tutor/tutorial/create", status_code=status.HTTP_201_CREATED)
    async def createTutorTutorial(self, request: Request):
        form_data = await request.form()
        payload = dict(form_data)
        isSample = form_data.get("isSample")
        category = form_data.get("category")
        tutorial_content = form_data.get("tutorial_content")
        tutorial_answer = form_data.get("tutorial_answer")
        payload['id'] = uuid.uuid4().hex
        # Save to db
        self.TutorHandler.__create_item__(payload)
        # Send mail to Student to Set his password
        user = self.TutorHandler.filterDb(email=payload['email']).first()
        if user:
            try:
                self.password_handler.set_password(payload)
                return APIMessage(
                    detail="Password set email successfully sent",
                    status_code=status.HTTP_200_OK
                )
            except:
                return APIMessage(
                       detail="Password email not sent",
                       status_code=status.HTTP_400_BAD_REQUEST
                    )
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    # Only Authenticated user and admin can delete Account
    @tutor_endpoint.delete("/tutor",   status_code=status.HTTP_200_OK)
    async def deleteTutor(self, payload:  Request):
        return self.tutor_handle.deleteTutor(await payload.json())

    @tutor_endpoint.patch("/tutor")
    async def patchTutor(self, payload: Request):
        return self.tutor_handle.patchTutor(await payload.json())

    @tutor_endpoint.put("/tutor")
    async def updateTutor(self, request: Request, payload: TutorSchema):
        return self.tutor_handle.updateTutor(payload.dict())

    @tutor_endpoint.post("/tutor/login")
    async def loginTutor(self, request: Request, payload: LoginSchema):
        return self.tutor_handle.loginTutor(payload.dict())
    
    @tutor_endpoint.post("/set/tutor/password")
    async def setPassword(self, request: Request, payload: ResetPasswordSchema):
        return self.tutor_handle.updatePassword(payload.dict())
    
    @tutor_endpoint.post("/reset/tutor/password")
    async def resetPassword(self, request: Request, payload: ResetPasswordSchema):
        return self.tutor_handle.resetPassword(
                    payload.dict()
                )
    
    @tutor_endpoint.get("/account/tutor/my/answers", status_code=status.HTTP_200_OK)
    def studentAsksQuestion(self, request: Request, _=Depends(manager)):
        return templates.TemplateResponse('tutor_answers.html', {"request": request})
    
    @tutor_endpoint.get("/top/tutors")
    def topTutors(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('top_tutors.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/tutorials/view")
    def ViewTutorials(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_tutorials.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/payments/view")
    def ViewPayments(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_payment.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/payments/withdraw")
    def WithdrawPayments(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_withdraw.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/support/request")
    def RequestSupport(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_support.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/profile/view")
    def TutorProfile(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_profile.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/password/update")
    def PasswordUpdateTutor(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_password_update.html', {"request": request})
    
    @tutor_endpoint.get("/tutor/emails/subscribe")
    def emailSubscriptionTutor(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_subscribe.html', {"request": request})
    

    @tutor_endpoint.get("/tutor/feedback/view")
    def tutorFeedbacks(self, request: Request):
        tutors = self.tutor_handle.getTutors()
        print(tutors)
        return templates.TemplateResponse('tutor_review.html', {"request": request})