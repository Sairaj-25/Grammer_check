from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from speechfix.core.database import Base

class User(Base):
    __tablename__ = "users"

    id =   Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # 0ne-to-many relationship: A user can save multiple questions
    questions = relationship("Question", back_populates="owner")

    
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    hint = Column(Text, nullable=True)
    topic_label = Column(String)
    difficulty_label = Column(String)

    # Foreign key linking back to the User
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="questions")
