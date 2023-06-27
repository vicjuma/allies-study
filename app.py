from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.utils import get_templates
from fastapi.exceptions import HTTPException

templates = get_templates()

app = FastAPI(
            title="StudyAllies - Get Your Best Solutions",
            version="0.0.1",
            contact = {
                    "name": "Victor Juma",
                    "url": "https://github.com/vicjuma",
                    "email": "vicjuma945@gmail.com"
                },
            license_info= {
                    "name": "mouseinc"
                }
        )

app.mount("/static", StaticFiles(directory="src/static"), name="static")

origins = [
    "http://127.0.0.1",
    "localhost",
    "http://127.0.0.1:8000",
    "https://encrypted-tbn0.gstatic.com/",
    "https://google.com",
    "https://www.google.com",
    "http://127.0.0.1:8000/student",
    "http://127.0.0.1:8887/",
    "http://127.0.0.1:3000/"
]

# Add cross origin middlewares

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from src.Employer import students_endpoint
from src.TaskService import task_endpoint
from src.Worker import tutor_endpoint
from src.SpecialitiesService import specialities_router
from src.SubjectService import subject_router
from src.invoiceService import invoice_router
from src.tutorSubject import tutorsubject_router
from src.Auth import shared_endpoint


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse('404.html', {"request": request})

app.include_router(students_endpoint)
app.include_router(task_endpoint)
app.include_router(tutor_endpoint)
app.include_router(specialities_router)
app.include_router(subject_router)
app.include_router(invoice_router)
app.include_router(tutorsubject_router)
app.include_router(shared_endpoint)
