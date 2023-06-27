from typing import Dict, Any
from src.models.models import Tutor
from src.utils import DatabaseStudentTableMixin, generate_password_hash, check_password_hash
from fastapi_restful.api_model import APIMessage
import uuid
from fastapi import (
    HTTPException,
    status
)
import os
# get the logins from environment Variables
PASSWORD = os.environ.get("PASSWORD")
SENDER_MAIL = os.environ.get("SENDER_MAIL")

class TutorHandler:
    def __init__(self):
        self.TutorHandler = DatabaseStudentTableMixin(Tutor)

    def getTutor(self, id):
        if self.TutorHandler[id]:
            return self.TutorHandler[id].to_json()
        return None

    def getTutors(self):
        return {
                'tutors': [
                        item.to_json() for item in self.TutorHandler if item is not None
                    ]
            }

    def createTutor(self, payload: Dict[str, Any]):
        # Check if user Exist 
        if self.TutorHandler.filterDb(email=payload['email']).first():
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already Exists"
                )
        else:
            payload['id'] = uuid.uuid4().hex
            self.TutorHandler.__createitem__(payload)
            # Send password set form to email
            created_worker = self.TutorHandler.filterDb(
                        email=payload['email']
                    ).first()
            return self.setPassword(created_worker.to_json())

    def deleteTutor(self, user_id: str, user: Dict[Any, str]):
        if self.TutorHandler[user_id]:
            if user["id"] == self.TutorHandler[user_id].id:
                del self.TutorHandler[user_id]
                return APIMessage(
                        detail="Tutor Deletion Success",
                        status_code=status.HTTP_200_OK
                    )
            raise HTTPException(
                        detail="Unauthorized access",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
        raise HTTPException(
                    detail="Tutor not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def updateTutor(self, payload: Dict[str, Any], user: Dict[str, Any]):
        user_id = payload["id"]
        
        if 'password'in payload:
            payload['password'] = generate_password_hash(payload['password'])

        worker = self.TutorHandler[user_id]
        
        if worker:
            if user['id'] == worker.id:
                worker = payload
                return self.TutorHandler[user_id].to_json()
            raise HTTPException(
                        detail="Unauthorized access",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
        raise HTTPException(
                    detail="Tutor not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def patchTutor(self, payload: Dict[str, Any], user: Dict[str, Any]):
        if 'password'in payload:
            payload['password'] = generate_password_hash(payload['password'])

        if "id" in payload.keys():
            user_id = payload['id']
            if self.TutorHandler[user_id]:
                # check for owner
                if user['id'] == self.TutorHandler[user_id].id:
                    self.TutorHandler.patchDb(payload)
                    return self.TutorHandler[user_id].to_json()
                raise HTTPException(
                            detail="Unauthorized access",
                            status_code=status.HTTP_403_FORBIDDEN
                        )
            raise HTTPException(
                        detail="Tutor not found",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
        raise HTTPException(
                detail="Id missing in payload",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def loginTutor(self, payload):
        # check if user exist
        user = self.TutorHandler.filterDb(email=payload["email"]).first()

        if user is not None:
            # check for passwordMatch
            if check_password_hash(payload["password"], user.password):
                return {
                    "token":  create_access_token(subject=user.id, expires_delta=120)
                }
            raise HTTPException(
                    ) 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tutor does not exist"
                )

    def setPassword(self, payload):
        user = self.TutorHandler.filterDb(email=payload['email']).first()
        if user:
            try:
                self.password_handler.set_password(user.to_json())
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

    def resetPassword(self, payload):
        # Get the use by email
        user = self.TutorHandler.filterDb(email=payload['email']).first()
        if user:
            try:
                self.password_handler.reset_password(user.to_json())
                return APIMessage(
                    detail="Reset email successfully sent",
                    status_code=status.HTTP_200_OK
                )
            except:
                return APIMessage(
                       detail="Reset email not sent",
                       status_code=status.HTTP_400_BAD_REQUEST
                    )
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
