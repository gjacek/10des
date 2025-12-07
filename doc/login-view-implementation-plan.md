# Plan implementacji widoku Logowania (Login View)

## 1. Przegląd

Widok logowania służy jako punkt wejścia do aplikacji dla użytkowników (Studentów i Prowadzących). Jego głównym celem jest uwierzytelnienie użytkownika za pomocą adresu e-mail i hasła, pobranie tokena JWT oraz przekierowanie do odpowiedniego pulpitu nawigacyjnego w zależności od roli użytkownika (Student lub Prowadzący). Widok wykorzystuje minimalistyczny styl Pico.css oraz Alpine.js do obsługi logiki po stronie klienta.

## 2. Routing widoku

*   **URL:** `/` (Strona główna aplikacji)
*   **Nazwa widoku Django:** `index` lub `login_view`
*   **Template:** `registration/login.html` (lub `pages/home.html` w zależności od struktury projektu, założono strukturę bazową).

## 3. Struktura komponentów

Widok składa się z głównego szablonu Django, który renderuje kontener HTML, oraz komponentu Alpine.js zarządzającego formularzem.

```text
BaseTemplate (base.html)
└── MainContainer (<main class="container">)
    └── AuthCard (article)
        ├── Header (hgroup: Tytuł i Podtytuł)
        └── LoginForm (form x-data="loginForm")
            ├── ErrorMessage (div x-show="error")
            ├── InputEmail (input type="email")
            ├── InputPassword (input type="password")
            ├── SubmitButton (button aria-busy="loading")
            └── FooterLinks (Reset hasła, Rejestracja)
```

## 4. Szczegóły komponentów

### `LoginForm` (Alpine.js Component)

*   **Opis:** Komponent reaktywny obsługujący stan formularza, walidację wstępną oraz komunikację z API.
*   **Główne elementy HTML:**
    *   `<form>` z dyrektywą `@submit.prevent="submit"`.
    *   Pola wejściowe korzystające z `x-model` do wiązania danych.
    *   Przycisk submit zmieniający stan wizualny podczas ładowania (`aria-busy`).
*   **Obsługiwane zdarzenia:**
    *   `submit`: Przechwycenie wysłania formularza, zablokowanie domyślnej akcji i wywołanie metody logowania.
    *   `input`: Czyszczenie komunikatów o błędach podczas wpisywania danych.
*   **Warunki walidacji:**
    *   Email: Wymagany, format adresu e-mail (HTML5 validation).
    *   Hasło: Wymagane, niepuste.
*   **Typy (Model danych w Alpine.js):**
    *   `formData`: Obiekt przechowujący `email` i `password`.
    *   `loading`: Boolean, flaga trwania żądania.
    *   `error`: String | null, treść błędu do wyświetlenia.
*   **Propsy (Atrybuty danych przekazywane z Django):**
    *   `data-next-student`: URL przekierowania dla studenta (np. `/student/my-courses/`).
    *   `data-next-instructor`: URL przekierowania dla prowadzącego (np. `/instructor/dashboard/`).

## 5. Typy

Poniższe definicje typów opisują struktury danych używane w komunikacji z API oraz wewnątrz komponentu.

### DTO (Data Transfer Objects)

**LoginRequest (JSON payload):**
```json
{
  "email": "string (format: email)",
  "password": "string (min_length: 1)"
}
```

**LoginResponse (JSON success):**
```json
{
  "token": "string (JWT)",
  "user": {
    "id": "integer",
    "email": "string",
    "is_instructor": "boolean"
  }
}
```

**ErrorResponse (JSON error):**
```json
{
  "detail": "string (Opis błędu)"
}
```

## 6. Zarządzanie stanem

Zarządzanie stanem odbywa się lokalnie w komponencie Alpine.js (`x-data`).

*   **Stan formularza:** Przechowywany w obiekcie `formData`.
*   **Stan UI:** Zmienne `isLoading` (do blokowania przycisku) oraz `errorMessage` (do wyświetlania alertów).
*   **Stan sesji:** Po pomyślnym zalogowaniu, token JWT jest zapisywany w `localStorage` pod kluczem `auth_token` (zgodnie z założeniem MVP, choć docelowo warto rozważyć HttpOnly cookies).

Definicja komponentu Alpine:
```javascript
function loginForm() {
    return {
        formData: {
            email: '',
            password: ''
        },
        isLoading: false,
        errorMessage: null,
        
        async submit() { ... }
    }
}
```

## 7. Integracja API

*   **Endpoint:** `POST /api/auth/login/`
*   **Nagłówki:**
    *   `Content-Type: application/json`
    *   `X-CSRFToken`: Pobierany z ciasteczka `csrftoken` (standard Django), wymagany dla bezpieczeństwa, nawet przy API.
*   **Metoda:** `fetch`
*   **Obsługa odpowiedzi:**
    *   **200 OK:** Parsowanie JSON, zapis tokena, sprawdzenie flagi `is_instructor`, przekierowanie.
    *   **401 Unauthorized:** Wyświetlenie komunikatu "Nieprawidłowy e-mail lub hasło".
    *   **Inne błędy:** Wyświetlenie ogólnego komunikatu "Wystąpił błąd serwera".

## 8. Interakcje użytkownika

1.  **Wypełnienie formularza:** Użytkownik wpisuje e-mail i hasło.
2.  **Próba wysłania (Błąd walidacji):** Jeśli pola są puste, przeglądarka blokuje wysyłkę (HTML5 validation).
3.  **Wysłanie formularza (Submit):**
    *   Przycisk zmienia stan na "ładowanie" (kręciołek/wyszarzenie).
    *   Formularz zostaje zablokowany.
4.  **Otrzymanie błędu (np. złe hasło):**
    *   Stan ładowania znika.
    *   Pojawia się czerwony baner z komunikatem błędu nad formularzem.
    *   Hasło (opcjonalnie) jest czyszczone.
5.  **Sukces:**
    *   Następuje przekierowanie strony (full page reload/redirect) do odpowiedniego dashboardu.

## 9. Warunki i walidacja

*   **Frontend (HTML5):**
    *   `<input type="email" required>`: Zapewnia podstawową poprawność formatu i wymagalność.
    *   `<input type="password" required>`: Zapewnia wymagalność.
*   **Frontend (Logic):**
    *   Blokada wielokrotnego wysłania formularza (zmienna `isLoading`).
*   **Backend (API):**
    *   Weryfikacja czy użytkownik istnieje.
    *   Weryfikacja poprawności hasła.
    *   Weryfikacja czy konto jest aktywne (`is_active`).

## 10. Obsługa błędów

*   **Błędy sieci (Network Error):** `try-catch` wokół `fetch` wyłapuje brak połączenia. Wyświetla komunikat: "Błąd połączenia. Spróbuj ponownie.".
*   **Błędy 4xx (Client):** Parsowanie odpowiedzi JSON i wyświetlanie pola `detail` lub domyślnego komunikatu "Błędne dane logowania".
*   **Błędy 5xx (Server):** Wyświetlenie komunikatu "Błąd serwera. Skontaktuj się z administratorem.".

## 11. Kroki implementacji

1.  **Szablon HTML:** Utworzenie pliku `templates/registration/login.html` (lub odpowiednika dla strony głównej) rozszerzającego `base.html`.
2.  **Struktura Pico.css:** Dodanie kontenera `<article>` wyśrodkowanego na stronie.
3.  **Formularz:** Dodanie pól input i przycisku zgodnie ze specyfikacją Pico.css.
4.  **Alpine.js Setup:**
    *   Zainicjowanie `x-data="loginForm()"` w tagu `<form>`.
    *   Dodanie `x-model` do inputów.
    *   Dodanie obsługi błędu (`x-show`).
5.  **Logika JS:** Zaimplementowanie funkcji `loginForm` w bloku `<script>` wewnątrz szablonu (lub w osobnym pliku JS).
    *   Implementacja `fetch` do API.
    *   Obsługa CSRF (funkcja pomocnicza `getCookie`).
    *   Logika przekierowań (pobranie URLi z atrybutów `data` lub zmiennych globalnych Django).
6.  **Integracja z Django Views:** Upewnienie się, że widok serwujący ten szablon przekazuje w kontekście (lub szablon hardcoduje) URLe docelowe (`student_dashboard_url`, `instructor_dashboard_url`).
7.  **Testy manualne:**
    *   Logowanie poprawne (Student/Prowadzący).
    *   Logowanie błędne.
    *   Próba logowania przy wyłączonym API.

