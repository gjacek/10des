# Plan implementacji widoku Rejestracji

## 1. Przegląd
Widok rejestracji umożliwia nowym użytkownikom (domyślnie Studentom) utworzenie konta w systemie. Formularz zbiera podstawowe dane osobowe oraz dane uwierzytelniające. Po pomyślnej rejestracji użytkownik jest przekierowywany do strony logowania.

## 2. Routing widoku
*   **Ścieżka URL:** `/register/`
*   **Nazwa widoku Django:** `register_view`
*   **Plik URLconf:** `kursy/urls.py`

## 3. Struktura komponentów
Widok jest oparty na szablonach Django (Server-Side Rendering) z interaktywnością zapewnianą przez Alpine.js.

*   `base.html` (Główny layout - istnieje)
    *   `register.html` (Szablon widoku rejestracji - do utworzenia)
        *   `RegisterForm` (Komponent logiczny Alpine.js - wewnątrz szablonu)
            *   Input: Imię (`first_name`)
            *   Input: Nazwisko (`last_name`)
            *   Input: E-mail (`email`)
            *   Input: Hasło (`password`)
            *   Button: "Zarejestruj się" (`submit`)
            *   Link: "Masz już konto? Zaloguj się"

## 4. Szczegóły komponentów

### `RegisterForm` (Alpine.js Component)
*   **Opis:** Główny kontener logiki formularza, obsługujący stan inputów, walidację po stronie klienta i komunikację z API.
*   **Główne elementy HTML:** Tag `<form>` z atrybutem `x-data="registerForm()"`.
*   **Obsługiwane zdarzenia:**
    *   `@submit.prevent="submit"`: Przechwycenie wysłania formularza.
    *   `@input`: Czyszczenie błędów walidacji przy edycji pola.
*   **Warunki walidacji:**
    *   `first_name`: Wymagane.
    *   `last_name`: Wymagane.
    *   `email`: Wymagane, format e-mail.
    *   `password`: Wymagane, min. 8 znaków (opcjonalnie, zależnie od konfiguracji backendu).
*   **Typy (ViewModel):** Patrz sekcja Typy.
*   **Propsy:** Brak (komponent strony głównej).

## 5. Typy

### ViewModel (Stan Alpine.js)
```typescript
interface RegisterViewModel {
  form: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  };
  errors: {
    first_name?: string[];
    last_name?: string[];
    email?: string[];
    password?: string[];
    detail?: string; // Ogólny błąd
  };
  isLoading: boolean;
  successMessage: string | null;
}
```

### DTO (Data Transfer Objects)

**Request (POST /api/auth/register/)**
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "password": "string"
}
```

**Response (Success - 201 Created)**
```json
{
  "id": integer,
  "email": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Response (Error - 400 Bad Request)**
```json
{
  "email": ["User with this email already exists."],
  "password": ["This field is required."]
}
```

## 6. Zarządzanie stanem
Stan jest lokalny dla widoku i zarządzany przez Alpine.js (`x-data`).
*   **Inicjalizacja:** Pusty formularz, brak błędów.
*   **Hooki:** Standardowa funkcja inicjalizująca komponent zwracająca obiekt danych (pattern fabryki w Alpine).

## 7. Integracja API
Komunikacja odbywa się z endpointem REST API.

*   **Endpoint:** `/api/auth/register/`
*   **Metoda:** `POST`
*   **Format:** JSON
*   **Headers:** `Content-Type: application/json`
*   **Obsługa odpowiedzi:**
    *   201 Created: Wyświetlenie komunikatu sukcesu, opóźnione przekierowanie na `/` (login).
    *   400 Bad Request: Przypisanie błędów z odpowiedzi do obiektu `errors` w stanie komponentu.
    *   500/Other: Wyświetlenie ogólnego komunikatu błędu.

## 8. Interakcje użytkownika
1.  **Wypełnianie formularza:** Użytkownik wpisuje dane. Błędy walidacji (jeśli istnieją) znikają podczas pisania w danym polu.
2.  **Kliknięcie "Zarejestruj się":**
    *   Przycisk zmienia stan na "disabled" i pokazuje spinner/tekst "Rejestracja...".
    *   Wysyłane jest żądanie do API.
3.  **Sukces:**
    *   Przycisk pozostaje zablokowany.
    *   Pojawia się komunikat "Konto utworzone pomyślnie. Przekierowanie do logowania...".
    *   Po 2 sekundach następuje przekierowanie na stronę główną (`/`).
4.  **Błąd formularza:**
    *   Przycisk wraca do stanu aktywnego.
    *   Pod odpowiednimi polami pojawiają się czerwone komunikaty błędów (np. "Ten e-mail jest już zajęty").
5.  **Nawigacja:** Kliknięcie linku "Zaloguj się" przenosi natychmiast na stronę logowania.

## 9. Warunki i walidacja
*   **Frontend:**
    *   Atrybuty HTML5 `required` dla podstawowej walidacji przeglądarki.
    *   Atrybut `type="email"` dla pola e-mail.
*   **Backend (API):**
    *   Unikalność adresu e-mail (krytyczne).
    *   Wymagalność wszystkich pól (`first_name`, `last_name` są `NOT NULL` w bazie).
    *   Siła hasła (według walidatorów Django).

## 10. Obsługa błędów
*   **Błędy walidacji (400):** Mapowanie kluczy z JSONa odpowiedzi na pola formularza. Jeśli klucz nie pasuje do pola (np. `non_field_errors`), wyświetlenie błędu nad formularzem.
*   **Błędy serwera (500) / Sieci:** Wyświetlenie generycznego komunikatu "Wystąpił błąd połączenia. Spróbuj ponownie później" nad formularzem.

## 11. Kroki implementacji

1.  **Backend - URL i Widok:**
    *   Dodać wpis `path('register/', views.register_view, name='register')` w `kursy/urls.py`.
    *   Utworzyć funkcję `register_view` w `kursy/views.py` renderującą szablon.

2.  **Frontend - Szablon:**
    *   Utworzyć plik `kursy/templates/registration/register.html`.
    *   Rozszerzyć `base.html`.
    *   Zaimplementować układ oparty na Pico.css (kontener, karta, formularz).

3.  **Frontend - Logika Alpine.js:**
    *   Zaimplementować skrypt z funkcją `registerForm()`.
    *   Dodać obsługę `fetch` do API.
    *   Dodać obsługę stanów `isLoading` i `errors`.

4.  **Testowanie:**
    *   Sprawdzić poprawną rejestrację (201).
    *   Sprawdzić walidację duplikatu e-maila (400).
    *   Sprawdzić walidację brakujących pól.

