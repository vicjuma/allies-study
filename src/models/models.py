from __future__ import annotations
from typing import Dict, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Boolean,
    DateTime,
    Text,
    Float
)
from sqlalchemy.orm import relationship, backref
import datetime
import random
import string

def generate_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

Base = declarative_base()

class Specialities(Base):
    __tablename__ = "specialities"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(100))
    students = relationship("Student", lazy="dynamic", backref=backref("speciality"))

    def to_json(self):
        return {
                "id": self.id,
                "name": self.name,
                "students": [
                        item.to_json() for item in self.students
                    ]
            }

class TutorSubject(Base):
    __tablename__ = "tutorsubject"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(200), nullable=False)
    tutors = relationship("Tutor", lazy="dynamic")


    def to_json(self):
        return {
                "id": self.id,
                "name": self.name,
                "tutors": [
                        item.to_json() for item in self.tutors
                    ]
            }


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250), default='')
    phone = Column(String(250))
    department = Column(String(250))
    about = Column(Text)
    speciality_id = Column(Integer, ForeignKey("specialities.id"))
    is_admin = Column(Boolean, default=False)
    time_zone = Column(String(250))
    task_created = relationship('Tasks', lazy='dynamic', backref=backref('creator'), cascade="all, delete-orphan")
    invoice = relationship("Invoice", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs) -> None:
        super(Student, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__qualname__}(username={self.username!r}, email={self.email!r}, phone={self.phone!r}, password={self.password!r}, account={self.account!r})'

    def to_json(self):
        return {
            "id": self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'password': self.password,
            'department': self.department,
            "is_admin": self.is_admin,
            "about": self.about,
            "speciality_id": self.speciality_id,
            "time_zone": self.time_zone,
            "task_created": [
                    item.to_json() for item in self.task_created
                ] 
        }


class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    suject_name = Column(String(150))
    tasks = relationship("Tasks", back_populates="subject")

    def to_json(self):
        return {
                "id": self.id,
                "subject_name": self.suject_name
            }


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    content = Column(Text)
    topics = Column(String(250), nullable=False)
    amount = Column(Float, nullable=False)
    deposit = Column(Float, default=0)
    feedback = Column(Text)
    title = Column(String(250), default=None)
    creator_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    attachment = relationship('TaskAttachment', lazy='dynamic', backref='task', cascade="all, delete-orphan")
    payment_status = Column(String(250), default='unpaid')
    progress_status = Column(String(250), default="unclaimed")
    tutor_id = Column(Integer, ForeignKey('tutor.id'))
    tutor = relationship("Tutor", back_populates="tasks")
    subject_id = Column(Integer, ForeignKey("subject.id"), default="Anonymous")
    subject = relationship("Subject", back_populates="tasks")
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    timeline = Column(DateTime, nullable=False)
    invoice = relationship("Invoice", lazy="dynamic", cascade="all, delete-orphan")
    answer = relationship("Solution", lazy="dynamic")
    bidders = relationship("Bidders", lazy="dynamic")
    notification = Column(Boolean, default=False)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(Amount={self.Amount}, creator id={self.creator_id})"

    
    def to_json(self):
        return {
            "id": self.id,
            "topics": self.topics,
            "Amount": self.amount,
            "deposit": self.deposit,
            "description": self.content,
            "creator_id": self.creator_id,
            "progress_status": self.progress_status,
            "title": self.title,
            "tutor_id": self.tutor_id,
            "payment_status": self.payment_status,
            "date_created": self.date_created,
            "feedback": self.feedback,
            "timeline": self.timeline,
            "answer": [
                    item.to_json() for item in self.answer
                ],
            "invoice": [
                    item.to_json() for item in self.invoice
                ],
            "bidders": [
                    item.to_json() for item in self.bidders
                ]
        }

class Solution(Base):
    __tablename__ = "solution"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description = Column(Text)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutor.id"), nullable=False)
    attachment = relationship("SolutionAttachment", lazy="dynamic")

    def to_json(self):
        return {
                "id": self.id,
                "task_id": self.task_id,
                "description": self.description,
                "tutor_id": self.tutor_id,
                "attachment": [
                        item.to_json() for item in self.attachment
                    ]
            }
    
class TaskAttachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    attachment_name = Column(String(250), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(task id = {self.task_id}, name={self.attachment_name})"
    
    def to_json(self):
        return {
                "id": self.id,
                "attachment_name": self.attachment_name,
                "task_id": self.task_id
            }
    

class TutorialAttachment(Base):
    __tablename__ = 'tutorial_attachment'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    attachment_name = Column(String(250), nullable=False)
    tutorial_id = Column(Integer, ForeignKey('tutorial.id'), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(tutorial id = {self.tutorial_id}, name={self.attachment_name})"
    
    def to_json(self):
        return {
                "id": self.id,
                "attachment_name": self.attachment_name,
                "task_id": self.tutorial_id
            }
    
class TutorialAnswerAttachment(Base):
    __tablename__ = 'tutorial_answer_attachment'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    attachment_name = Column(String(250), nullable=False)
    tutorial_answer_id = Column(Integer, ForeignKey('tutorial.id'), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(tutorial_answer id = {self.tutorial_answer_id}, name={self.attachment_name})"
    
    def to_json(self):
        return {
                "id": self.id,
                "attachment_name": self.attachment_name,
                "task_id": self.tutorial_answer_id
            }




class SolutionAttachment(Base):
    __tablename__ = "solutionattachment"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    file_name = Column(String(200))
    solution_id = Column(Integer, ForeignKey("solution.id"))

    def to_json(self):
        return {
                "id": self.id,
                "file_name": self.file_name,
                "solution_id": self.solution_id
            }


class Tutor(Base):
    __tablename__ = 'tutor'
    id = Column(Integer, primary_key=True, autoincrement=True, default=10000, nullable=False)
    username = Column(String(250))
    password = Column(String(250))
    about = Column(Text)
    email = Column(String(250))
    account = Column(Float, nullable=False, default=0.00)
    phone = Column(String(250))
    department = Column(String(250))
    rating = Column(Integer, default=0)
    speciality_id = Column(String(150))
    tasks = relationship('Tasks', lazy='dynamic')
    solutions = relationship("Solution", lazy="dynamic")
    bids = relationship("Bidders", lazy="dynamic")
    subject_id = Column(Integer, ForeignKey("tutorsubject.id"))

    def __repr__(self):
        return f"{self.__class__.__qualname__}(" \
               f"id={self.id}, username={self.username})"

    def to_json(self):
        return {
            "id": self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'account': self.account,
            'phone': self.phone,
            "department": self.department,
            "about": self.about,
            "rating": self.rating,
            "subject_id": self.subject_id,
            "tasks": [
                    item.to_json() for item in self.tasks
                ],
            "tasks": [
                    item.to_json() for item in self.tasks
                ],
            "bids": [
                    item.to_json() for item in self.bids
                ]
        }

class Bidders(Base):
    __tablename__ = "bidders"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("tutor.id"))

    def to_json(self):
        return {
                "id": self.id,
                "task_id": self.task_id,
                "user_id": self.user_id
            }

class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    invoice_date = Column(DateTime, default=datetime.datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    payment_status = Column(String(150), default="unpaid")
    due_date = Column(DateTime, nullable=False,
            default = datetime.datetime.now() + datetime.timedelta(hours=24)
        )
    transaction = relationship("Transaction", lazy="dynamic", cascade="all, delete-orphan")

    def to_json(self):
        return {
                "id": self.id,
                "invoice_date": self.invoice_date,
                "amount": self.amount,
                "task_id": self.task_id,
                "payment_status": self.payment_status,
                "due_date": self.due_date,
                "user_id": self.user_id,
                "transaction": [
                        item.to_json() for item in self.transaction
                    ]
            }


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code = Column(String(250), nullable=False)
    transaction_date = Column(
            DateTime,
            nullable=False,
            default=datetime.datetime.utcnow
        )
    invoice_id = Column(
            Integer,
            ForeignKey("invoice.id")
        )

    def to_json(self):
        return {
                "id": self.id,
                "code": self.code,
                "transaction_date": self.transaction_date,
                "invoice_id": self.invoice_id
            }
    

class Tutorial(Base):
    __tablename__ = "tutorial"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    posted_date = Column(DateTime, default=datetime.datetime.utcnow)
    isPurchased = Column(Boolean, default=False)
    title = Column(Text, nullable=False)
    category_name = Column(String(150), nullable=False)
    price = Column(Integer, nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutor.id"), nullable=False)
    actions = Column(Text)
    tutorial_content = Column(Text, nullable=False)
    tutorial_answer = Column(Text, nullable=False)
    isSample = Column(Boolean, default=False)
    tutorial_attachment = relationship('TutorialAttachment', lazy='dynamic', backref='tutorial', cascade="all, delete-orphan")
    tutorial_answer_attachment = relationship('TutorialAnswerAttachment', lazy='dynamic', backref='tutorial_answer', cascade="all, delete-orphan")

    def to_json(self):
        return {
                "id": self.id,
                "posted_date": self.posted_date,
                "purchased": self.isPurchased,
                "title": self.title,
                "tutor_id": self.tutor_id,
                "price": self.price,
                "category_name": self.category_name,
                "actions": self.actions,
                "isSample": self.isSample,
                "tutorial_content": self.tutorial_content,
                "tutorial_answer": self.tutorial_answer
            }


