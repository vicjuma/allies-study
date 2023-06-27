from src.models import (
    ContextManager,
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY
)
from fastapi import HTTPException
from collections.abc import MutableMapping
from sqlalchemy import update, insert
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Dict, Union, Any
from fastapi.templating import Jinja2Templates
import random
import string

ALGORITHM = "HS256"

REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_templates():
    return Jinja2Templates("src/templates")

# Password Encoding and Decoding
def generate_password_hash(password: str) -> str:
    return password_context.hash(password)


def check_password_hash(password: str, hashed_passd: str) -> bool:
    return password_context.verify(password, hashed_passd)

def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def create_access_token(subject) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=2, minutes=30),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': subject
        }
        return jwt.encode(
            payload, 
            JWT_SECRET_KEY,
            algorithm=ALGORITHM
        )


def decode_access_token(token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


class DatabaseTableMixin(MutableMapping):
    def __init__(self, table):
        self.table = table

    def __getitem__(self, id):
        return self.filter({'id': id}).first()

    def __setitem__(self, key, value) -> Dict[str, str]:
        with ContextManager() as context:
            statement = update(self.table).where(
                        self.table.id == key
                    ).values(**value)

            context.session.execute(statement)
            context.commit()
        return value
    
    def __iter__(self):
        with ContextManager() as context:
            for elements in context.session.query(self.table):
                yield elements

    def filter(self, kwargs):
        with ContextManager() as context:
            return context.session.query(self.table).filter_by(**kwargs)

    def __len__(self):
        with ContextManager() as context:
            return context.session.query(self.table).count()

    def __delitem__(self, key):
        instance = self[key]
        with ContextManager() as context:
            context.session.delete(instance)
            context.commit()
    
    def __create_item__(self, payload):
        with ContextManager() as context:
            statement = insert(self.table).values(
                    **payload
                    )
            context.session.execute(statement)
            context.session.commit()

    def filterDb(self, **payload):
        with ContextManager() as context:
            out_ = context.session.query(self.table).filter_by(**payload)
        return out_

    def patchDb(self, payload):

        item_id = payload['id']
        
        with ContextManager() as context:
            item = context.session.query(self.table).filter_by(id=item_id).first()
            
            for key, val in payload.items():
                if hasattr(item, key):
                    setattr(item, key, val)
            context.session.commit()
        return payload

class DatabaseStudentTableMixin(DatabaseTableMixin):
    def __getitem__(self, identifier):
        # Check if the identifier is an email
        student = self.filter({'email': identifier}).first()
        if student:
            return student

        # If not found, assume it's a username
        return self.filter({'username': identifier}).first()

class DatabaseCombinedTableMixin(DatabaseTableMixin):
    def __init__(self, table1, table2):
        self.table1 = table1
        self.table2 = table2
    def __getitem__(self, identifier):
        user = self.filter({'email': identifier}).first()
        return user
    



