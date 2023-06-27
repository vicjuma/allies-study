from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from fastapi import (
    Depends,
    Request
)
from typing import (
    Dict,
    Any
)
from src.tutorSubject.utils import TutorSubjectHandler

tutorsubject_router = InferringRouter()

@cbv(tutorsubject_router)
class SubjectService:
    def __init__(self):
        self.subject_handler = TutorSubjectHandler()
    
    @tutorsubject_router.post("/create/tutor/subject")
    async def createSubject(self, payload: Request):
        return self.subject_handler.createSubject(await payload.json())

    @tutorsubject_router.get("/get/tutor/subjects")
    def getSubjects(self):
        return self.subject_handler.getSubjects()

    @tutorsubject_router.get("/subjects/{subject_id}")
    def getSubjectById(self, subject_id: str):
        return self.subject_handler.getSubjectById(subject_id)


