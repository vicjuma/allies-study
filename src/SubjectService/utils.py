from src.utils import DatabaseTableMixin
from fastapi import (
    HTTPException,
    status
)
import uuid
from src.models.models import Subject
from fastapi_restful.api_model import APIMessage 
from typing import (
    Dict,
    Any
)
class SubjectHandler:
    def __init__(self):
        self.subject_mixin = DatabaseTableMixin(Subject)

    def createSubject(self, payload: Dict[str, Any], user: Dict[str, Any]):
        # if user['is_admin'] == True:
        # payload['id'] = uuid.uuid4().hex
        self.subject_mixin.__create_item(**payload)
        return payload
        # raise HTTPException(
        #         detail="UnAuthorized Access",
        #         status_code=status.HTTP_403_FORBIDDEN
        #     )

    def getSubject(self, subject_id):
        if self.subject_mixin[subject_id]:
            return self.subject_mixin[subject_id].to_json()
        raise HTTPException(
                    detail="Subject not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def getSubjects(self):
        return {
                "subjects":[
                        item.to_json() for item in iter(self.subject_mixin)
                    ]
            }

    def updateSubject(self, payload: Dict[str, Any], user: Dict[str, Any]):
        if user['is_admin'] == True:
            if self.subject_mixin[payload['id']]:
                self.subject_mixin[payload['id']] = payload
                return payload
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subject not found"
                )
        raise HTTPException(
                detail="Unauthorized Access",
                status_code=status.HTTP_403_FORBIDDEN
            )

    def deleteSubject(self, payload: Dict[str, Any], user: Dict[str, Any]):
        if user.is_admin == True:
            if self.subject_mixin[payload['id']]:
                del self.subject_mixin[payload['id']]
                return APIMessage(
                        detail="Subject delete success",
                        status_code=status.HTTP_200_OK
                    )
            raise HTTPException(
                    detail="subject Not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        raise HTTPException(
                detail="Unauthorized access",
                status_code=status.HTTP_403_FORBIDDEN
            )
