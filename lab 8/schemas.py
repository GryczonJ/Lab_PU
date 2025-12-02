# schemas.py
from pydantic import BaseModel, Field

class MovieBase(BaseModel):
    tytul: str = Field(..., example="Władca Pierścieni: Drużyna Pierścienia")
    gatunek: str = Field(None, example="Fantasy")
    dostepny_do_wypozyczenia: bool = Field(True, example=True)
    ile_egzemplarzy: int = Field(1, example=5)

class MovieCreate(MovieBase):
    pass

class MovieUpdate(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int = Field(..., example=1)

    model_config = {
        "from_attributes": True
    }
