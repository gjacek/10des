# Plan implementacji szablonu bazowego (Base Template)

## 1. Przegląd

Szablon `base.html` stanowi szkielet HTML dla wszystkich podstron aplikacji. Zapewnia spójny układ graficzny oparty na **Pico.css**, ładuje niezbędne biblioteki (Alpine.js), definiuje globalną nawigację (Navbar) reagującą na stan uwierzytelnienia (JWT w `localStorage`) oraz udostępnia kontenery na komunikaty systemowe (Toasts) i główną treść.

## 2. Lokalizacja pliku

*   **Ścieżka:** `templates/base.html`
*   **Struktura katalogów:** Należy upewnić się, że w `settings.py` skonfigurowano `DIRS` dla `TEMPLATES`.

## 3. Struktura komponentów

Szablon definiuje strukturę dokumentu HTML5.

```text
Document (html)
├── Head
│   ├── Meta tags (charset, viewport)
│   ├── Title Block ({% block title %})
│   ├── CSS Links (Pico.css, Custom CSS)
│   ├── Alpine.js (Script defer)
│   └── Global Styles (x-cloak definition)
└── Body (class="container-fluid" lub elastyczny layout)
    ├── Navbar (nav x-data="authStore")
    │   ├── Brand/Logo
    │   └── MenuLinks (Zależne od roli)
    ├── ToastContainer (div fixed)
    ├── MainContent (main class="container")
    │   └── Django Block ({% block content %})
    ├── Footer (footer)
    └── Scripts Block ({% block extra_js %})
```

## 4. Szczegóły komponentów

### `Head` i Biblioteki
*   **Pico.css:** Ładowany z CDN (wersja minimalna) lub pliku statycznego. Zapewnia responsywność i style domyślne.
*   **Alpine.js:** Ładowany z CDN. Służy do obsługi stanu nawigacji, dropdownów i globalnego stanu auth.
*   **Font:** Domyślny systemowy stack czcionek (zgodnie z filozofią Pico).

### `Navbar` (Komponent Alpine.js)
*   **Opis:** Pasek nawigacyjny zmieniający się dynamicznie w zależności od tego, czy użytkownik posiada token JWT i jaką ma rolę.
*   **Atrybuty:** `x-data` odwołujące się do globalnego store'a (np. `Alpine.store('auth')`).
*   **Logika wyświetlania:**
    *   **Gość:** Widzi Logo, link "Zaloguj" i "Zarejestruj".
    *   **Student:** Widzi Logo, "Moje Kursy", "Dostępne Kursy", Dropdown Użytkownika (Wyloguj).
    *   **Prowadzący:** Widzi Logo, "Dashboard", Dropdown Użytkownika (Wyloguj).
*   **Elementy interaktywne:**
    *   Przycisk Wyloguj: Wywołuje funkcję czyszczącą `localStorage` i przekierowującą na stronę główną.

### `ToastContainer`
*   **Opis:** Kontener umieszczony w prawym górnym lub dolnym rogu (position: fixed), wyświetlający powiadomienia.
*   **Integracja:** Nasłuchuje na globalne zdarzenie `window` (np. `dispatch('notify', {message, type})`).

### `MainContent`
*   **Opis:** Główny kontener `main` z klasą `container` (marginesy i centrowanie), w którym renderowane są widoki Django poprzez tag `{% block content %}`.

## 5. Typy i Dane Globalne

Mimo że jest to HTML, Alpine.js będzie operował na strukturze danych użytkownika przechowywanej w przeglądarce.

### AuthUser (w LocalStorage)
```javascript
{
  "token": "string (JWT)",
  "user": {
    "id": number,
    "email": "string",
    "is_instructor": boolean,
    "first_name": "string",
    "last_name": "string"
  }
}
```

## 6. Zarządzanie stanem (Alpine.js Store)

W pliku `base.html` (lub dołączonym `main.js`) należy zainicjować globalny store Alpine do zarządzania tożsamością.

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.store('auth', {
        user: null,
        token: null,
        
        init() {
            // Pobranie danych z localStorage przy starcie
            this.token = localStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data');
            if (userData) this.user = JSON.parse(userData);
        },
        
        get isLoggedIn() { return !!this.token; },
        get isInstructor() { return this.user?.is_instructor || false; },
        get isStudent() { return this.user && !this.user.is_instructor; },

        logout() {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            this.token = null;
            this.user = null;
            window.location.href = '/'; // Przekierowanie do logowania
        }
    });
});
```

## 7. Integracja API (Globalna)

Szablon bazowy powinien dołączyć prosty skrypt narzędziowy (`api-client.js` lub inline), który:
1.  Przechwytuje każde wywołanie `fetch` (opcjonalnie wrapper).
2.  Dodaje nagłówek `Authorization: Bearer <token>` jeśli token istnieje.
3.  Nasłuchuje odpowiedzi `401 Unauthorized` i w razie wystąpienia wymusza wylogowanie (`auth.logout()`).

## 8. Interakcje użytkownika

*   **Nawigacja:** Kliknięcie w linki (zwykłe tagi `<a>`, gdyż routing jest po stronie serwera Django).
*   **Wylogowanie:** Kliknięcie przycisku "Wyloguj" -> wyczyszczenie stanu -> odświeżenie strony/przekierowanie.
*   **Responsywność:** Na mobilkach menu może zwijać się do "hamburgera" (standard Pico.css lub prosty toggle w Alpine).

## 9. Warunki i walidacja

*   **x-cloak:** Należy dodać styl `[x-cloak] { display: none !important; }`, aby ukryć elementy nawigacji (np. przyciski Dashboardu) zanim Alpine.js załaduje stan z localStorage. Zapobiegnie to miganiu niewłaściwego interfejsu.
*   **CSRF:** W sekcji `<head>` należy umieścić tag `<meta name="csrf-token" content="{{ csrf_token }}">` dla potrzeb zapytań POST wykonywanych przez JS (np. logout, choć ten jest tutaj client-side, ale inne formularze mogą tego wymagać).

## 10. Obsługa błędów

*   **Brak JS:** Aplikacja powinna wyświetlić komunikat `<noscript>`, informujący o konieczności włączenia JavaScript, ponieważ kluczowe funkcje (logowanie, interakcja API) polegają na Alpine.js.

## 11. Kroki implementacji

1.  **Struktura plików:** Utworzenie katalogu `templates` w głównym katalogu projektu i pliku `base.html`.
2.  **Konfiguracja Django:** Dodanie `'DIRS': [BASE_DIR / 'templates']` w `settings.py`.
3.  **HTML Skeleton:** Wklejenie boilerplate'u HTML5.
4.  **CDN Links:** Dodanie linków do Pico.css i Alpine.js w `<head>`.
5.  **CSS Fixes:** Dodanie stylów dla `[x-cloak]` i ewentualnych nadpisań (np. stopka przyklejona do dołu - `sticky footer`).
6.  **Alpine Store:** Zaimplementowanie skryptu inicjalizującego `Alpine.store('auth')` przed zamknięciem `<body>`.
7.  **Navbar Implementation:**
    *   Stworzenie tagu `<nav>`.
    *   Dodanie logiki `x-show` lub `x-if` opartej na `Alpine.store('auth').isLoggedIn`.
    *   Zdefiniowanie linków dla poszczególnych ról.
8.  **Blocks:** Dodanie `{% block content %}` wewnątrz `<main>` oraz bloków na skrypty i style.
9.  **Toast Notification Setup:** Dodanie puste kontenera na powiadomienia i prostego skryptu obsługującego zdarzenie `window.dispatchEvent(new CustomEvent('notify', ...))`.

