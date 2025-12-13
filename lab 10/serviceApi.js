import { Movie } from './model.js';

export const API_BASE_URL = "http://127.0.0.1:8000/filmy/";

/**
 * Konwertuje obiekt otrzymany z API do instancji klasy Movie.
 * UWAGA: Pola zmienione na zgodne z modelem DB (tytul, gatunek, itd.)
 * @param {object} apiObject
 * @returns {Movie}
 */
const movieFromApi = (apiObject) => {
    return new Movie(
        apiObject.id,
        apiObject.tytul,                 
        apiObject.gatunek,              
        apiObject.dostepny_do_wypozyczenia, 
        apiObject.ile_egzemplarzy       
    );
};

const cleanMovie = (m) => {
    return new Movie(
        m.id,
        m.tytul?.trim(),
        m.gatunek?.trim(),
        m.dostepny_do_wypozyczenia,
        m.ile_egzemplarzy
    );
};

// --- CREATE (Dodawanie) ---
export async function createMovie(movie) {
    const response = await fetch(API_BASE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(movie.toApiObject()),
    });

    if (!response.ok) {
        // Rzucenie wyjątku z informacją o błędzie
        throw new Error(`Błąd tworzenia filmu: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return cleanMovie(movieFromApi(data));

}

// --- READ ALL (Pobieranie wszystkich) ---
export async function readMovies(skip = 0, limit = 100) {
    const url = `${API_BASE_URL}?skip=${skip}&limit=${limit}`;
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Błąd pobierania filmów: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.map(m => cleanMovie(movieFromApi(m)));
}

// --- READ ONE (Pobieranie pojedynczego) ---
export async function readMovie(movieId) {
    const url = `${API_BASE_URL}${movieId}`;
    const response = await fetch(url);

    if (response.status === 404) {
        return null; 
    }
    if (!response.ok) {
        throw new Error(`Błąd pobierania filmu o ID ${movieId}: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return cleanMovie(movieFromApi(data));
}

// --- UPDATE (Aktualizacja) ---
export async function updateMovie(movieId, movieUpdate) {
    const url = `${API_BASE_URL}${movieId}`;
    
    const response = await fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(movieUpdate.toApiObject()),
    });

    if (!response.ok) {
        throw new Error(`Błąd aktualizacji filmu o ID ${movieId}: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return cleanMovie(movieFromApi(data));

}

// --- DELETE (Usuwanie) ---
export async function deleteMovie(movieId) {
    const url = `${API_BASE_URL}${movieId}`;
    const response = await fetch(url, {
        method: 'DELETE',
    });

    if (response.status === 404) {
        return false;
    }
    if (!response.ok && response.status !== 204) {
        throw new Error(`Błąd usuwania filmu o ID ${movieId}: ${response.status} ${response.statusText}`);
    }
    
    return true;
}