from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = 'vacancis'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    alternate_url = Column(String, nullable=False)
    area_name = Column(String, nullable=False)
    professional_roles = Column(String, nullable=False)
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
