from fastapi_restful.cbv import cbv
import uuid
from fastapi_restful.inferring_router import InferringRouter
from fastapi import (
        Depends,
        Request
    )
from src.utils import DatabaseTableMixin, get_templates
from src.SubjectService.utils import SubjectHandler
from typing import (
        Dict,
        Any
    )
from src.models.schema import SubjectSchema
from src.models.models import Subject

subject_router = InferringRouter()

@cbv(subject_router)
class SubjectService:
    def __init__(self):
        self.subject_handler = SubjectHandler()
        self.subject_mixin = DatabaseTableMixin(Subject)
    
    @subject_router.get("/subject")
    async def createSubject(self):
        subjects = ["John",
        "Accounting",
        "Algebra",
        "Applied Sciences",
        "Architecture and Design",
        "Art & Design",
        "Biology",
        "Business & Finance",
        "Calculus",
        "Chemistry",
        "Communications",
        "Computer Science",
        "Economics",
        "Engineering",
        "English",
        "Environmental Science",
        "Article Writing",
        "Film",
        "Foreign Languages",
        "Geography",
        "Geology",
        "Geometry",
        "Health & Medical",
        "History",
        "HR Management",
        "Information Systems",
        "Law",
        "Literature",
        "Management",
        "Marketing",
        "Math",
        "Numerical Analysis",
        "Philosophy",
        "Physics",
        "Precalculus",
        "Political Science",
        "Psychology",
        "Programming",
        "Science",
        "Social Science",
        "Statistics"
        ]
        for subject in subjects:
            self.subject_mixin.__create_item__({"suject_name": subject})
        return {"message": "all subjects created successfully"}
    
    @subject_router.patch("/subject")
    async def updateSubject(self, payload: Request):
        return self.subject_handler.updateSubject(payload)
    
    @subject_router.get("/subjects")
    def getsubjects(self):
        return self.subject_handler.getSubjects()
    
    @subject_router.get("/subject/{subject_id}")
    def getSubject(self, subject_id: str):
        return self.subject_handler.getSubject(subject_id)

    @subject_router.delete("/subject")
    async def deleteSubject(self, payload: Request):
        return self.subject_handler.deleteSubject(payload)
