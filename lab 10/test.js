// D:\konda\envs\lab-pu\Lab_PU\lab 10\test.js

import { Movie } from './model.js'; 
import { 
    createMovie, 
    readMovies, 
    readMovie, 
    updateMovie, 
    deleteMovie,
    API_BASE_URL // <--- Zmienione: importujemy API_BASE_URL
} from './serviceApi.js';

async function runTests() {
    console.log("--- START TESTÓW API FILMÓW ---");

    let createdMovieId;
    let testMovieTytul = "Testowy Film CRUDA"; // Zmieniono nazwę zmiennej dla czytelności
    let testMovieGatunek = "Science Fiction";
    
    try {
        // 1. CREATE (Dodawanie)
        console.log("\n1. Dodawanie nowego filmu...");
        const newMovie = new Movie(null, testMovieTytul, testMovieGatunek, true, 2);
        
        const createdMovie = await createMovie(newMovie);
        createdMovieId = createdMovie.id;
        console.log("-> Utworzono film:", createdMovie);
        console.assert(createdMovie.tytul.trim() === testMovieTytul.trim(), 
               "Błąd w CREATE: Tytuł się nie zgadza.");
        
        // 2. READ ALL (Pobieranie listy)
        console.log("\n2. Pobieranie listy filmów (limit 5)...");
        const moviesList = await readMovies(0, 5);
        console.log(`-> Pobrano ${moviesList.length} filmów.`);
        console.assert(moviesList.length > 0, "Błąd w READ ALL: Lista jest pusta.");
        
        // 3. READ ONE (Pobieranie pojedynczego)
        console.log(`\n3. Pobieranie filmu o ID: ${createdMovieId}...`);
        const readOneMovie = await readMovie(createdMovieId);
        console.log("-> Odczytano film:", readOneMovie);

        console.assert(readOneMovie && readOneMovie.tytul === testMovieTytul, "Błąd w READ ONE: Nie odnaleziono lub dane się nie zgadzają.");
        
        // 4. UPDATE (Aktualizacja)
        console.log(`\n4. Aktualizacja filmu o ID: ${createdMovieId}...`);
        const nowyTytul = "Film Aktualizowany 2025 (OK)";
        const nowyGatunek = "Thriller";
  
        const updatedData = new Movie(createdMovieId, nowyTytul, nowyGatunek, false, 1);
        
        const updatedMovie = await updateMovie(createdMovieId, updatedData);
        console.log("-> Zaktualizowano film:", updatedMovie);
  
        console.assert(updatedMovie.tytul === nowyTytul, "Błąd w UPDATE: Tytuł nie został zaktualizowany.");
        console.assert(updatedMovie.dostepny_do_wypozyczenia === false, "Błąd w UPDATE: Dostępność nie została zaktualizowana.");
        
        // 5. DELETE (Usuwanie)
        console.log(`\n5. Usuwanie filmu o ID: ${createdMovieId}...`);
        const isDeleted = await deleteMovie(createdMovieId);
        console.log(`-> Czy usunięto: ${isDeleted}`);
        console.assert(isDeleted === true, "Błąd w DELETE: Film nie został usunięty.");

        
        const deletedCheck = await readMovie(createdMovieId);
        console.assert(deletedCheck === null, "Błąd w DELETE: Film nadal istnieje po usunięciu.");
        console.log("-> Weryfikacja usunięcia: OK.");

    } catch (error) {
        console.error("\n--- BŁĄD PODCZAS TESTÓW ---");
        console.error(error);
        
        console.log("Upewnij się, że serwer FastAPI jest uruchomiony na:", API_BASE_URL);
    } finally {
        console.log("\n--- KONIEC TESTÓW API FILMÓW ---");
    }
}


runTests();