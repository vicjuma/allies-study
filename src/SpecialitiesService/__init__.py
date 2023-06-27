from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from fastapi import (
    Depends,
    status,
    Request
)
from typing import (
    Any,
    Dict
)
from src.models.schema import SpecialitySchema
from src.SpecialitiesService.utils import SpecialitiesHandler

specialities_router = InferringRouter()

@cbv(specialities_router)
class SpecialitiesService:
    def __init__(self):
        self.specialities_handler = SpecialitiesHandler()
    
    @specialities_router.get("/specialities")
    def getSpecialities(self):
        return self.specialities_handler.getSpecialities()

    @specialities_router.get("/specialities/{speciality_id}")
    def getSpecialitiesById(self, speciality_id: str):
        return self.specialities_handler.getSpeciality(speciality_id)

    @specialities_router.post("/specialities")
    async def createSpecialities(self, request: Request, payload: SpecialitySchema):
        return self.specialities_handler.createSpecialities(payload.dict())
    
    @specialities_router.patch("/specialities")
    async def updateSpecialities(self, payload: Request):
        return self.specialities_handler.updateSpeciality(await payload.json())

    @specialities_router.delete("/specialities")
    async def deleteSpecialities(self, payload: Request):
        return self.specialities_handler.deleteSpecialities(await payload.json())
