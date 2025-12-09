# Plan implementacji szablonu bazowego (Base Template)

## 1. Przegląd

Szablon `base.html` stanowi szkielet HTML dla wszystkich podstron aplikacji. Zapewnia spójny układ graficzny oparty na **Pico.css**, ładuje niezbędne biblioteki (Alpine.js), definiuje globalną nawigację (Navbar) reagującą na stan uwierzytelnienia (renderowany przez Django) oraz udostępnia kontenery na komunikaty systemowe (Toasts) i główną treść.

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
*   **Opis:** Pasek nawigacyjny renderowany przez Django na podstawie `request.user`. Alpine.js może zarządzać tylko interaktywnością (np. dropdown na mobile).
*   **Logika wyświetlania:** Wykorzystuje tagi szablonu `{% if user.is_authenticated %}` oraz `{% if user.is_instructor %}`.
*   **Logika wyświetlania:**
    *   **Gość:** Widzi Logo, link "Zaloguj" i "Zarejestruj".
    *   **Student:** Widzi Logo, "Moje Kursy", "Dostępne Kursy", Dropdown Użytkownika (Wyloguj).
    *   **Prowadzący:** Widzi Logo, "Dashboard", Dropdown Użytkownika (Wyloguj).
*   **Elementy interaktywne:**
    *   Przycisk Wyloguj: Formularz POST do `/logout/` (standard Django) lub link wywołujący wylogowanie.

### `ToastContainer`
*   **Opis:** Kontener umieszczony w prawym górnym lub dolnym rogu (position: fixed), wyświetlający powiadomienia.
*   **Integracja:** Nasłuchuje na globalne zdarzenie `window` (np. `dispatch('notify', {message, type})`).

### `MainContent`
*   **Opis:** Główny kontener `main` z klasą `container` (marginesy i centrowanie), w którym renderowane są widoki Django poprzez tag `{% block content %}`.

## 5. Typy i Dane Globalne

Dane użytkownika są dostępne w szablonie jako zmienna `user`. Można je przekazać do Alpine.js (jeśli potrzebne) za pomocą filtra `json_script`.

## 6. Zarządzanie stanem

Stan uwierzytelnienia jest zarządzany przez sesję Django. Nie jest wymagany globalny store Alpine.js do przechowywania tokena.
Jeśli potrzebna jest interaktywność zależna od roli w JS (np. ukrywanie elementów bez przeładowania), można zainicjować prosty store:

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.store('auth', {
        // Wartości wstrzyknięte z szablonu, np. <script id="auth-data" type="application/json">...</script>
        isLoggedIn: document.body.dataset.auth === 'true',
    });
});
```

## 7. Integracja API (Globalna)

Szablon bazowy powinien dołączyć prosty skrypt narzędziowy (`api-client.js` lub inline), który:
1.  Przechwytuje każde wywołanie `fetch` (opcjonalnie wrapper).
2.  Dodaje nagłówek `X-CSRFToken` pobrany z ciasteczka `csrftoken` (dla metod POST/PUT/PATCH/DELETE).
3.  Nasłuchuje odpowiedzi `401/403` i w razie wystąpienia przekierowuje na login.

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

