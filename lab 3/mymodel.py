# Utwórz na lokalnym serwerze MS SQL pustą bazę Biblioteka. W wykorzystaniem
# SQLAlchemy stwórz model (plik mymodel.py) z klasą Ksiazka zawierającą obowiązkowe
# pola angielski_tytul i angielskie_streszczenie.
# Z wykorzystaniem Alembic utwórz dla modelu migrację i strukturę bazy na serwerze:
#  - inicjując Alembic przez alembic init alembic
# - w pliku alembic.ini podaj w sqlalchemy.url connection string do bazy Biblioteka
#  - w pliki env.py odszukaj target_metadata i wpisz:
# from mymodel import Base
# target_metadata = Base.metadata
#  - utwórz migrację i wygeneruj bazę:
#  alembic revision --autogenerate -m "DodanieModeluKsiazka"
#  alembic upgrade head 


from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ksiazka(Base):
    """Model SQLAlchemy reprezentujący książkę."""
    __tablename__ = 'ksiazki'

    id = Column(Integer, primary_key=True)
    
    # Zmieniona nazwa zmiennej: Tytul (pozostaje obowiązkowe)
    title = Column(String(255), nullable=False, unique=True)
    
    # Zmieniona nazwa zmiennej: Streszczenie (pozostaje obowiązkowe)
    summary = Column(Text, nullable=False)

    polskie_streszczenie = Column(Text, nullable=True)
    
    def __repr__(self):
        # Zaktualizowano odniesienie do zmiennej w metodzie repr
            return f"<Ksiazka(id={self.id}, title='{self.title}', summary='{self.summary}', polskie_streszczenie='{self.polskie_streszczenie}')>"
