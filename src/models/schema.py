from __future__ import annotations
from pydantic import BaseModel, Field
import datetime
from typing import (
    List,
    Optional,
    Any
)
from enum import Enum
from fastapi import Form


class PaymentStatus(str, Enum):
    paid = "paid"
    unpaid = "unpaid"


class TaskStatus(str, Enum):
    complete = "claimed"
    incomplete = "unclaimed"
    pending = "pending"


class BidSchema(BaseModel):
    id: str
    task_id: str
    user_id: str


class SpecialitySchema(BaseModel):
    name: str

class PaymentSchema(BaseModel):
    name: str
    phone_number: int
    email:str
    currency: str
    comment: Optional[str]


class MassPayDisburseSchema(BaseModel):
    details: List[PaymentSchema]


class TransactionSchema(BaseModel):
    id: str
    code: str
    transaction_date: datetime.datetime
    invoice_id: str


class ResetPasswordSchema(BaseModel):
    email: str


class CreateInvoiceSchema(BaseModel):
    task_id: str
    amount: float


class InvoiceSchema(BaseModel):
    id: str
    invoice_date: datetime.datetime
    task_id: str
    amount: float
    user_id: str
    payment_status: PaymentStatus
    due_date: datetime.datetime
    transaction: Optional[List[TransactionSchema]]


class InvoicesSchema(BaseModel):
    invoices: List[InvoiceSchema]


class CreateStudentSchema(BaseModel):
    username: str
    email: str
    password: str

class DeletionSchema(BaseModel):
    status: str

class TokenSchema(BaseModel):
    status: str


class StudentSchema(BaseModel):
    id: str
    username: str
    email: str
    phone: Optional[str]
    department: str
    password: Optional[str]
    about: Optional[str]
    speciality_id: Optional[str]
    is_admin: bool
    time_zone: Optional[str]
    task_created: Optional[List[Any]]

class NoRecords(BaseModel):
    message: str = Field(default="No records found")


class StudentsSchema(BaseModel):
    students: List[StudentSchema]


class SubjectSchema(BaseModel):
    id: str
    subject_name: str


class CreateTaskAttachmentSchema(BaseModel):
    task_id: str


class TaskAttachmentSchema(BaseModel):
    id: str
    attachment_name: str
    task_id: str


class CreateSolutionAttachmentSchema(BaseModel):
    solution_id: str


class SolutionAttachmentSchema(BaseModel):
    id: str
    file_name: str
    solution_id: str


class SolutionSchema(BaseModel):
    id: str
    description: str
    task_id: str
    tutor_id: str
    attachment: Optional[List[SolutionAttachmentSchema]]


class TaskIdSchema(BaseModel):
    id: str

class CreateTaskSchema(BaseModel):
    description: str
    Amount: float
    deposit: float
    title: str
    subject_id: str


class TaskSchema(BaseModel):
    id: str
    content: str
    topics: str
    amount: float
    deposit: float
    feedback: Optional[str]
    title: Optional[str]
    creator_id: str
    payment_status: PaymentStatus
    progress_status: TaskStatus
    tutor_id: Optional[str]
    subject_id: Optional[str]
    subject: Optional[List[SubjectSchema]]
    date_created: datetime.datetime
    timeline: datetime.datetime
    answer: Optional[List[SolutionSchema]]
    invoice: Optional[List[InvoiceSchema]]
    bidders: Optional[List[BidSchema]]
    notification: bool


class TasksSchema(BaseModel):
    tasks: List[TaskSchema]


class CreateWorkerSchema(BaseModel):
    name: str
    email: str
    
class TutorSchema(BaseModel):
    id: str
    username: str
    email: str
    phone: str
    department: str
    about:str
    rating: int
    password: Optional[str]
    tasks: List[TaskSchema]
    bids: Optional[List[BidSchema]]


class TutorsSchema(BaseModel):
    tutors: List[TutorSchema]


class LoginSchema(BaseModel):
    email: str
    password: str
