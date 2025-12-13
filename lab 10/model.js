// D:\konda\envs\lab-pu\Lab_PU\lab 10\model.js (Zaktualizowana wersja)

/**
 * @class Movie
 * Reprezentuje obiekt filmu używany w usłudze REST.
 */
export class Movie {
    /**
     * @param {number | null} id - Identyfikator filmu (może być null przy tworzeniu).
     * @param {string} tytul - Tytuł filmu.
     * @param {string} gatunek - Gatunek filmu (opcjonalny).
     * @param {boolean} [dostepny_do_wypozyczenia=true] - Czy film jest dostępny.
     * @param {number} [ile_egzemplarzy=1] - Liczba dostępnych kopii.
     */
    constructor(id, tytul, gatunek, dostepny_do_wypozyczenia = true, ile_egzemplarzy = 1) {
        this.id = id;
        this.tytul = tytul;
        this.gatunek = gatunek;
        this.dostepny_do_wypozyczenia = dostepny_do_wypozyczenia;
        this.ile_egzemplarzy = ile_egzemplarzy;
    }

    /**
     * Zwraca obiekt gotowy do wysłania w ciele zapytania POST/PUT.
     * @returns {object}
     */
    toApiObject() {
        // Obiekt do wysłania musi zawierać tylko te pola, które są w Pydantic (bez ID)
        const { id, ...apiObject } = this;
        return apiObject;
    }
}