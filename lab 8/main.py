# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Movie
from schemas import MovieRead, MovieCreate, MovieUpdate
from database import get_db


app = FastAPI(
    title="Wypożyczalnia Filmów API",
    description="Usługa REST CRUD na pojedynczej tabeli 'filmy'."
)

# --- CREATE ---
@app.post("/filmy/", response_model=MovieRead, status_code=status.HTTP_201_CREATED, tags=["Filmy"])
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# --- READ ALL ---
# @app.get("/filmy/", response_model=List[MovieRead], tags=["Filmy"])
# def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return db.query(Movie).offset(skip).limit(limit).all()'
@app.get("/filmy/", response_model=List[MovieRead], tags=["Filmy"])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Odczytuje listę filmów."""
    
    # 💡 KOREKTA: DODANIE KLAUZULI ORDER BY (sortowanie po ID)
    movies = (
        db.query(Movie)
        .order_by(Movie.id)  # Wymagane przez MS SQL przy użyciu OFFSET/LIMIT
        .offset(skip)
        .limit(limit)
        .all()
    )
    return movies

# --- READ ONE ---
@app.get("/filmy/{movie_id}", response_model=MovieRead, tags=["Filmy"])
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film nie został znaleziony")
    return movie

# --- UPDATE ---
@app.put("/filmy/{movie_id}", response_model=MovieRead, tags=["Filmy"])
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film nie został znaleziony")
    update_data = movie.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# --- DELETE ---
@app.delete("/filmy/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Filmy"])
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film nie został znaleziony")
