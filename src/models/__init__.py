from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from src.models.models import Base
from dotenv import load_dotenv

load_dotenv(
    os.path.join(
        os.path.abspath(
                os.path.dirname(
                    __file__
                    )
            ),
        "dbconfig.env"
    )        
)

# jwt token validation
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']
ACCESS_TOKEN_EXPIRE_MINUTES= 120

# Database Config
database_name = os.environ.get('DB_NAME')
database_password = os.environ.get('DB_PASSWD')
database_author = os.environ.get('DB_AUTHOR')

Base.metadata.create_all(
   create_engine(
       f'mysql+pymysql://{database_author}:{database_password}@localhost/{database_name}'
  )
)


class ContextManager:
    def __init__(self):
        self.databasefilename: str = f'mysql+pymysql://{database_author}:{database_password}@localhost/{database_name}'
        self.engine = create_engine(self.databasefilename)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
            self.session.close()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


