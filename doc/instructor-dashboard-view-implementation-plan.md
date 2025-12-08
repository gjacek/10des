# Plan implementacji widoku Dashboard Prowadzącego

## 1. Przegląd
Widok Dashboardu Prowadzącego jest centralnym punktem zarządzania dla użytkowników z rolą Prowadzącego. Umożliwia przegląd wszystkich prowadzonych kursów, szybką ocenę ich statusu (widoczność, liczba oczekujących studentów) oraz dostęp do kluczowych akcji: edycji kursu, zarządzania lekcjami oraz zarządzania zapisami. Widok jest renderowany po stronie serwera (Django Templates) z elementami interaktywnymi (JavaScript) do obsługi szybkich akcji.

## 2. Routing widoku
*   **Ścieżka URL:** `/instructor/dashboard/`
*   **Nazwa URL (Django):** `instructor_dashboard`
*   **Wymagania:** Użytkownik musi być zalogowany i posiadać rolę Prowadzącego (`is_instructor=True`).

## 3. Struktura komponentów
Struktura oparta na szablonach Django (MVT):

*   `BaseTemplate` (layout aplikacji)
    *   `InstructorDashboardView` (Główny kontener widoku)
        *   `DashboardHeader` (Tytuł + Przycisk "Utwórz nowy kurs")
        *   `InstructorCourseTable` (Tabela z listą kursów)
            *   `CourseRow` (Wiersz tabeli dla pojedynczego kursu)
                *   `CourseInfo` (Nazwa, Edycja)
                *   `PendingRequestsBadge` (Licznik oczekujących)
                *   `VisibilityToggle` (Komponent JS: Przełącznik widoczności)
                *   `ActionButtons` (Linki: Edytuj, Lekcje, Zapisy)

## 4. Szczegóły komponentów

### `InstructorDashboardView` (Widok Django / Szablon)
*   **Opis:** Główny widok renderujący całą stronę dashboardu.
*   **Główne elementy:**
    *   Nagłówek strony z przyciskiem akcji.
    *   Kontener tabeli kursów.
    *   Mechanizm paginacji (opcjonalnie, w MVP może być lista wszystkich).
*   **Obsługiwane interakcje:** Ładowanie strony, nawigacja do innych widoków.
*   **Obsługiwana walidacja:** Sprawdzenie uprawnień (LoginRequired, IsInstructor).
*   **Typy (Context Data):**
    *   `courses`: Lista obiektów `CourseViewModel`.
*   **Propsy:** Brak (to widok top-level).

### `InstructorCourseTable` (Fragment Szablonu)
*   **Opis:** Tabela HTML wyświetlająca listę kursów.
*   **Główne elementy:**
    *   `<thead>`: Kolumny (Nazwa kursu, Edycja, Status widoczności, Oczekujący, Akcje).
    *   `<tbody>`: Iteracja po liście kursów i renderowanie `CourseRow`.
*   **Obsługiwane interakcje:** Brak bezpośrednich (kontener).

### `CourseRow` (Fragment Szablonu)
*   **Opis:** Wiersz reprezentujący pojedynczy kurs.
*   **Główne elementy:**
    *   Komórki tabeli z danymi kursu.
    *   `VisibilityToggle` (input checkbox + skrypt JS).
    *   Linki do akcji (Edycja: `/instructor/courses/<id>/edit/`, Lekcje: `/instructor/courses/<id>/lessons/`, Zapisy: `/instructor/courses/<id>/enrollments/`).
*   **Obsługiwane interakcje:** Kliknięcia w linki akcji.

### `VisibilityToggle` (Komponent JS/HTML)
*   **Opis:** Interaktywny przełącznik (checkbox) zmieniający pole `is_visible` kursu bez przeładowania strony.
*   **Główne elementy:**
    *   `<input type="checkbox">` stylizowany na toggle switch.
    *   Atrybuty data: `data-course-id`, `data-initial-status`.
*   **Obsługiwane interakcje:**
    *   `change`: Wywołuje żądanie API PATCH.
*   **Obsługiwana walidacja:**
    *   Obsługa błędów API (np. brak uprawnień, błąd serwera) - przywrócenie stanu przełącznika i wyświetlenie komunikatu (Toast/Alert).

## 5. Typy

### `CourseViewModel` (Django Context Object)
Obiekt przekazywany do szablonu dla każdego kursu:
*   `id`: `int` (ID kursu)
*   `name`: `str` (Nazwa kursu)
*   `edition`: `str` (Nazwa edycji, np. "Zima 2024")
*   `is_visible`: `bool` (Status widoczności)
*   `pending_count`: `int` (Liczba oczekujących próśb o dołączenie - adnotacja z zapytania)
*   `detail_url`: `str` (URL do edycji/szczegółów)
*   `lessons_url`: `str` (URL do zarządzania lekcjami)
*   `enrollments_url`: `str` (URL do zarządzania zapisami)

### `VisibilityPatchRequest` (API DTO)
Struktura żądania JSON wysyłana przez JS:
*   `is_visible`: `bool`

## 6. Zarządzanie stanem

### Server-Side State (Django)
*   Stan główny (lista kursów) jest pobierany z bazy danych przy każdym załadowaniu strony (`request`).
*   Dane są przekazywane przez `context` do szablonu.

### Client-Side State (JavaScript)
*   Stan lokalny ogranicza się do komponentu `VisibilityToggle`.
*   Skrypt przechowuje stan `loading` podczas wykonywania zapytania API, aby zablokować wielokrotne kliknięcia.
*   Po błędzie API, stan UI jest cofany do stanu sprzed kliknięcia.

## 7. Integracja API

### Pobieranie danych (Initial Load)
*   Bezpośrednie zapytanie ORM w widoku Django (`Course.objects.filter(instructor=request.user)`).
*   Dane renderowane w HTML, nie przez API REST.

### Aktualizacja Widoczności (`VisibilityToggle`)
*   **Endpoint:** `PATCH /api/courses/{id}/`
*   **Metoda:** `PATCH`
*   **Headers:**
    *   `Content-Type: application/json`
    *   `X-CSRFToken`: (pobrany z ciasteczka lub tagu w szablonie)
*   **Body:** `{"is_visible": true/false}`
*   **Odpowiedź sukcesu:** `200 OK` (zaktualizowany obiekt kursu)
*   **Odpowiedź błędu:** `400 Bad Request`, `403 Forbidden`, `500 Server Error`.

## 8. Interakcje użytkownika

1.  **Wejście na Dashboard:**
    *   Użytkownik wchodzi na `/instructor/dashboard/`.
    *   Widzi tabelę swoich kursów.
2.  **Zmiana widoczności kursu:**
    *   Użytkownik klika przełącznik "Widoczny/Ukryty".
    *   Przełącznik wizualnie zmienia stan.
    *   W tle wysyłane jest żądanie API.
    *   Jeśli sukces: wyświetla się małe powiadomienie (opcjonalnie).
    *   Jeśli błąd: przełącznik wraca do poprzedniej pozycji, wyświetla się alert błędu.
3.  **Zarządzanie Zapisami:**
    *   Użytkownik widzi licznik w kolumnie "Oczekujący".
    *   Klika przycisk "Zapisy", przenosząc się do widoku szczegółowego zapisów.
4.  **Tworzenie kursu:**
    *   Użytkownik klika przycisk "Utwórz nowy kurs".
    *   Zostaje przeniesiony do formularza tworzenia kursu.

## 9. Warunki i walidacja

*   **Dostęp do widoku:** Tylko użytkownicy z `is_instructor=True`.
*   **Widoczność danych:** Prowadzący widzi TYLKO swoje kursy (filtrowanie po `instructor_id`).
*   **Toggle Widoczności:**
    *   System musi walidować, czy użytkownik jest właścicielem kursu (po stronie API).
    *   Token CSRF musi być poprawny dla żądań AJAX.

## 10. Obsługa błędów

*   **Brak uprawnień:** Przekierowanie do strony logowania lub 403 Forbidden.
*   **Błąd API (Toggle):**
    *   UI: Wyświetlenie komunikatu "Nie udało się zmienić statusu kursu".
    *   UI: Automatyczne cofnięcie zmiany w checkboxie (revert UI state).
*   **Pusty Dashboard:** Jeśli prowadzący nie ma kursów, wyświetlany jest zachęcający komunikat "Nie masz jeszcze żadnych kursów. Utwórz pierwszy!".

## 11. Kroki implementacji

1.  **Backend (Views):** Utworzenie klasy `InstructorDashboardView` (dziedziczącej po `LoginRequiredMixin`, `TemplateView` lub `ListView`).
2.  **Backend (Query):** Implementacja zapytania pobierającego kursy zalogowanego instruktora wraz z adnotacją liczby oczekujących (`Count('enrollments', filter=Q(enrollments__status='pending'))`).
3.  **Template (HTML):** Stworzenie szablonu `instructor_dashboard.html` dziedziczącego po `base.html`.
4.  **Template (Table):** Implementacja struktury tabeli i pętli po kursach.
5.  **Frontend (JS):** Napisanie prostego skryptu JS do obsługi `VisibilityToggle` (nasłuchiwanie `change`, `fetch` do API, obsługa błędów).
6.  **Routing:** Dodanie ścieżki w `urls.py`.
7.  **Testy:** Weryfikacja wyświetlania poprawnej listy kursów oraz działania przełącznika widoczności.

