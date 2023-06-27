from src.utils import DatabaseTableMixin
from src.models.models import (
    TutorSubject
)
from typing import (
        Dict,
        Any
)
from fastapi import (
        HTTPException,
        status
    )


class TutorSubjectHandler:
    def __init__(self):
        self.tutorsubject_handler = DatabaseTableMixin(TutorSubjectHandler)

    def createTutorTask(self, payload: Dict[str, Any], user: Dict[str, Any]):
        self.tutorsubject_handler.__create_item__(**payload)
        return payload

    def getSubjects(self):
        return {
                "subjects": [
                        item.to_json() for item in iter(self.tutorsubject_handler)
                    ]
            }

    def getSubjectById(self, subject_id):
        return self.tutorsubject_handler[subject_id].to_json()
