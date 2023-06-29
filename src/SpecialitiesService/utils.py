from fastapi import (
    status,
    HTTPException
)
from src.utils import DatabaseTableMixin
from src.models.models import Specialities
from typing import (
        List,
        Dict,
        Any
)
import uuid
from fastapi_restful.api_model import APIMessage

class SpecialitiesHandler:
    def __init__(self):
        self.specialities_handler = DatabaseTableMixin(Specialities)

    def createSpecialities(self, payload: Dict[str, Any]):
        # payload['id'] = uuid.uuid4().hex
        self.specialities_handler.__create_item__(payload)
        return payload

    def getSpecialities(self):
        return {
                "specialities": [
                    item.to_json() for item in iter(self.specialities_handler)
                    ]
            }

    def getSpeciality(self, speciality_id: str) -> Dict[str, Any]:
        if self.specialities_handler[speciality_id]:
            return self.specialities_handler[speciality_id].to_json()
        raise HTTPException(
                    detail="Speciality not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def updateSpeciality(self, payload: Dict[str, Any], user: Dict[str, Any]):
        task = self.specialities_handler[user['id']]
        if task:
            task = payload
            return payload
        raise HTTPException(
                    detail="Speciality not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

    def deleteSpecialities(self, payload: Dict[str, Any], user: Dict[str, Any]):
        speciality_id = payload['id']
        
        # Check for the Authenticated user
        if user['is_admin'] == True:
            if self.specialities_handler[speciality_id]:
                del self.specialities_handler[speciality_id]
                return APIMessage(
                        detail="Speciality delete success",
                        status_code=status.HTTP_200_OK
                    )
            raise HTTPException(
                        detail="Speciality not found",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
        raise HTTPException(
                    detail="UnAuthorized Access, Contact the Administrator",
                    status_code=status.HTTP_403_FORBIDDEN
                )
