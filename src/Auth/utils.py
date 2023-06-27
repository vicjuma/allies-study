from src.utils import DatabaseCombinedTableMixin
from src.models.models import Student, Tutor
from src.Worker.utils import (
        TutorHandler,
    )
from src.Employer.utils import StudentHandler


class SharedHandler:
    def __init__(self):
        self.sharedHandler = DatabaseCombinedTableMixin(Student, Tutor)
        self.tutor_handler = TutorHandler()
        self.student_handler = StudentHandler()
        self.payload = None

    def getBoth(self, identifier):
        user = None
        if self.student_handler.getStudent(identifier) is None:
            user = self.tutor_handler.getTutor(identifier)
        else:
            user = self.student_handler.getStudent(identifier)
        return user