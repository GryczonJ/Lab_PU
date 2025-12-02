from sqlalchemy import Boolean, Column, Integer, String
from pydantic import BaseModel, Field
from database import Base


# --- Definicja Modelu SQLAlchemy ORM ---
class Movie(Base):
    __tablename__ = "filmy"

   
    id = Column(Integer, primary_key=True, index=True)
    tytul = Column(String(255), index=True, nullable=False)
    gatunek = Column(String(100))
    
    dostepny_do_wypozyczenia = Column(Boolean, default=True, nullable=False)
    ile_egzemplarzy = Column(Integer, default=1, nullable=False)
    
    