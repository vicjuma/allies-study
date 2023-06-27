from typing import Dict, Any
from src.models.models import Student, Tutor
from src.utils import (
        DatabaseTableMixin,
        DatabaseStudentTableMixin,
        generate_password_hash,
        check_password_hash,
        create_access_token
)
from fastapi_restful.api_model import APIMessage
from fastapi import status, HTTPException
import uuid
import random
import string

def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

class StudentHandler:
    def __init__(self):
        self.employerHandler = DatabaseStudentTableMixin(Student)

    def getStudent(self, identifier):
        payload = None
        student_data = self.employerHandler[identifier]
        if student_data:
            task_created = student_data.task_created
            if not isinstance(task_created, list):
                task_created = None
            payload = {
                "id": student_data.id,
                "username": student_data.username,
                "email": student_data.email,
                "phone": student_data.phone,
                "password": student_data.password,
                "about": student_data.about,
                "speciality_id": student_data.speciality_id,
                "is_admin": student_data.is_admin,
                "time_zone": student_data.time_zone,
                "task_created": task_created
            }
        return payload

    def getStudents(self):
        return {
                'students': [
                        item.to_json() for item in self.employerHandler
                    ]
            }

    def createStudent(self, payload):
        # check if the user Exists in the database
        form_data = payload.form()
        username = form_data.get("username")
        email = form_data.get("email")
        user_email = self.employerHandler.filterDb(email=email).first()
        user_name = self.employerHandler.filterDb(username=username).first()
        
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
            self.employerHandler.__create_item__(payload)
            payload['password'] = password

            # Send mail to Student to Set his password
            return self.setPassword(payload)

    def updatePassword(self, payload):
        user = self.employerHandler[payload['id']]

        if user:
            if 'password' in payload:
                payload['password'] = generate_password_hash(payload['password'])
            self.employerHandler.patchDb(payload)
            return APIMessage(
                    status=status.HTTP_200_OK,
                    detail="user update success"
                )
        raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist"
                )

    def deleteStudent(self, user_id, user):
        employer = self.employerHandler[user_id]

        if employer:
            if user['id'] == user_id or user['is_admin'] == True:
                del employer
                return APIMessage(
                            detail="Student Deletion success",
                            status_code=status.HTTP_200_OK
                        )
            raise HTTPException(
                        detail="Unauthorized  Access",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
        raise HTTPException(
                    detail="Student not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def updateStudent(self, payload: Dict[str, Any], user):
        user_id = payload["id"]

        if 'password'in payload:
            payload['password'] = generate_password_hash(payload['password'])

        if user_id:
            if user['id'] == user_id or user[is_admin] == True:
                employer = self.employerHandler[user_id]
                if employer:
                    employer = payload
                    return employer.to_json()
                raise HTTPException(
                            detail="Student not found",
                            status_code=status.HTTP_404_NOT_FOUND
                        )
            raise HTTPException(
                        detail="Unauthorized access",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
        raise HTTPException(
                    detail="Student with such Id does not exist",
                    status_code=status.HTTP_4O4_NOT_FOUND
                )

    def patchStudent(self, payload: Dict[str, Any], user: Dict[str, Any]):
        if 'password'in payload:
            payload['password'] = generate_password_hash(payload['password'])

        if payload['id']:
            employer = self.employerHandler[payload["id"]]
            if employer:
                if employer.id == user['id'] or user['is_admin'] == True:
                    self.employerHandler.patchDb(payload)
                    return employer.to_json()
                raise HTTPException(
                            detail="Unauthorized access",
                            status_code=status.HTTP_404_NOT_FOUND
                        )
            raise HTTPException(
                        detail="Employer with such id does not exist",
                        status_code=status.HTTP_404_NOT_FOUND
                    )

        else:
            raise HTTPException(
                    detail="Missing id in Payload",
                    status=status.HTTP_400_BAD_REQUEST
                )

    def loginStudent(self, payload):
        # check if user exist
        student = self.employerHandler.filterDb(email=payload["email"]).first()

        if student is not None:
            # check for passwordMatch
            if check_password_hash(payload["password"], student.password):
                return {
                    "token":  create_access_token(subject=student.id)
                }
            else:
                raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Enter the Correct Credentials"
                        )
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User does not exist"
                )

    def setPassword(self, payload):
        user = self.employerHandler.filterDb(email=payload['email']).first()
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

    def resetPassword(self, payload):
        # Get the use by email
        user = self.employerHandler.filterDb(email=payload['email']).first()
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

class TokenHandler:
    def __init__(self):
        self.employerHandler = DatabaseTableMixin(Student)
        self.tutorHandler = DatabaseTableMixin(Tutor)
    
    def getStudent(self, id):
        payload = None
        student_data = self.employerHandler[id]
        if student_data:
            task_created = student_data.task_created
            if not isinstance(task_created, list):
                task_created = None
            payload = {
                "id": student_data.id,
                "username": student_data.username,
                "email": student_data.email,
                "phone": student_data.phone,
                "password": student_data.password,
                "about": student_data.about,
                "speciality_id": student_data.speciality_id,
                "is_admin": student_data.is_admin,
                "time_zone": student_data.time_zone,
                "task_created": task_created
            }
        return payload
    
    def getTutor(self, id):
        payload = None
        tutor_data = self.tutorHandler[id]
        if tutor_data:
            payload = {
            "id": tutor_data.id,
            'username': tutor_data.username,
            'password': tutor_data.password,
            'email': tutor_data.email,
            'account': tutor_data.account,
            'phone': tutor_data.phone,
            "about": tutor_data.about,
            "rating": tutor_data.rating,
            "subject_id": tutor_data.subject_id,
            "tasks": tutor_data.tasks,
            "bids": tutor_data.bids
        }
        return payload
