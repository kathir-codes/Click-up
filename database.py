
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean, #Represents a database column that stores TRUE or FALSE.
    DateTime,#Represents a database column that stores a date and time.
    String,#Represents a database column that stores text.
    create_engine,#The engine manages how SQLAlchemy communicates with your PostgreSQL database.
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

load_dotenv()

# ---------------------- Database Connection ----------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


def get_connection():
    return SessionLocal()


# ---------------------- User Profile Model ----------------------

class Base(DeclarativeBase): #Base as a common parent for all your database models.
    pass


class UserProfile(Base):    #A database model defines the table structure in Python before SQLAlchemy uses it to create the table.we create a DB model so SQLAlchemy knows how your database table is structured.  
    __tablename__ = "user_profiles" #You define the table structure using a Python class: Then you can create a Python object and ask SQLAlchemy to save it:

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


# ---------------------- Create User Profiles Table ----------------------

def create_user_profiles_table():
    Base.metadata.create_all(bind=engine) #metadata means information about your database tables and their structure.


# ---------------------- Insert User Profile ----------------------

def create_user_profile(
    user_id,
    name,
    email,
    email_verified=False,
):
    session = get_connection()

    try:
        user = UserProfile(
            id=user_id,
            name=name,
            email=email,
            email_verified=email_verified,
        )

        session.add(user)
        session.commit()

        return user.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# def update_user_email_verified(user_id, verified=True):
#     session = get_connection()

#     try:
#         user = session.get(UserProfile, user_id)

#         if user is None:
#             return False

#         user.email_verified = verified
#         session.commit()
#         return True

#     except Exception:
#         session.rollback()
#         raise

#     finally:
#         session.close()

def get_user_profile(user_id):
    session = get_connection()

    try:
        return session.get(UserProfile, user_id)
    finally:
        session.close()