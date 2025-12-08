# Plan implementacji widoku Zarządzanie Lekcjami

## 1. Przegląd
Widok "Zarządzanie Lekcjami" umożliwia instruktorom przeglądanie listy lekcji w ramach konkretnego kursu. Pozwala na szybkie zarządzanie statusem publikacji (robocza/opublikowana), usuwanie lekcji oraz nawigację do formularza dodawania/edycji lekcji. Jest to kluczowy widok w panelu instruktora, zapewniający kontrolę nad dostępnością materiałów dla studentów.

## 2. Routing widoku
*   **Ścieżka:** `/instructor/courses/<int:course_id>/lessons/`
*   **Nazwa URL:** `instructor_course_lessons`
*   **Widok Django:** `CourseLessonsView` (Class-Based View)

## 3. Struktura komponentów
Widok oparty jest na szablonach Django (Server-Side Rendering) z elementami interaktywnymi (Alpine.js) dla akcji asynchronicznych.

*   `BaseTemplate` (Layout główny)
    *   `CourseHeader` (Informacje o kursie: Nazwa, powrót do listy kursów)
    *   `LessonManagementContainer`
        *   `ActionToolbar` (Przycisk "Dodaj lekcję")
        *   `LessonTable` (Główna tabela danych)
            *   `LessonRow` (Wiersz lekcji - iterowany)
                *   `PublishToggle` (Komponent interaktywny statusu)
                *   `DeleteAction` (Przycisk usuwania z potwierdzeniem)

## 4. Szczegóły komponentów

### `LessonManagementContainer`
*   **Opis:** Główny kontener strony, pobiera i przekazuje listę lekcji do tabeli.
*   **Główne elementy:** Nagłówek sekcji, `ActionToolbar`, `LessonTable`.
*   **Propsy (Context):**
    *   `course`: Obiekt kursu (tytuł, ID).
    *   `lessons`: QuerySet lekcji (z adnotacją liczby plików).

### `LessonTable`
*   **Opis:** Tabela wyświetlająca listę lekcji.
*   **Główne elementy:** Tabela HTML (`<table>`), nagłówki kolumn (Tytuł, Status, Pliki, Akcje).
*   **Obsługiwane interakcje:** Sortowanie (opcjonalnie, domyślnie po tytule).

### `LessonRow` (Alpine.js Component: `x-data="lessonRow(id, initialStatus)"`)
*   **Opis:** Reprezentuje pojedynczą lekcję. Obsługuje logikę interakcji dla danego wiersza.
*   **Główne elementy:**
    *   Tytuł (link do edycji/szczegółów).
    *   Licznik plików (badge).
    *   `PublishToggle`.
    *   Przyciski akcji (Edytuj, Usuń).
*   **Obsługiwane interakcje:**
    *   `toggleStatus()`: Przełącza status publikacji.
    *   `deleteLesson()`: Inicjuje proces usuwania.
*   **Propsy (atrybuty data):**
    *   `lesson-id`: ID lekcji.
    *   `initial-status`: Stan początkowy (true/false).

### `PublishToggle`
*   **Opis:** Przełącznik (switch) zmieniający status `is_published`.
*   **Główne elementy:** Input typu checkbox (wizualnie toggle), etykieta statusu (Opublikowana/Robocza).
*   **Obsługiwane zdarzenia:** `change` -> wywołuje `toggleStatus` w rodzicu.
*   **Warunki walidacji:** Brak (zmiana zawsze dozwolona dla instruktora).

### `ActionToolbar`
*   **Opis:** Pasek narzędzi nad tabelą.
*   **Główne elementy:** Przycisk "Dodaj lekcję" (Link do `/instructor/courses/<id>/lessons/create/`).

## 5. Typy

### `LessonViewModel` (Context Django)
Model danych przekazywany do szablonu:
```python
class LessonViewModel:
    id: int
    title: str
    is_published: bool
    files_count: int  # Adnotacja z Count('attachments')
    updated_at: datetime
```

### `LessonDTO` (API Interaction)
Format danych wysyłany/odbierany podczas akcji asynchronicznych (Toggle):
```typescript
interface LessonPatchRequest {
    is_published: boolean;
}

interface LessonResponse {
    id: number;
    title: string;
    is_published: boolean;
}
```

## 6. Zarządzanie stanem
Zarządzanie stanem odbywa się hybrydowo:
1.  **Inicjalizacja:** Stan początkowy renderowany przez Django (`lessons` w context).
2.  **Klient (Alpine.js):**
    *   Lokalny stan wiersza: `isPublished` (inicjowany z atrybutu HTML).
    *   Stan operacji: `isProcessing` (blokada UI podczas requestu).
    *   Hooki: Brak złożonych hooków, logika zawarta w `x-data`.

## 7. Integracja API
Widok korzysta z REST API do akcji "w tle" bez przeładowania strony.

*   **Zmiana statusu (Toggle):**
    *   **Endpoint:** `PATCH /api/courses/{course_id}/lessons/{lesson_id}/`
    *   **Payload:** `{ "is_published": boolean }`
    *   **Response:** `200 OK` (zaktualizowany obiekt) lub `403/400`.
    *   **Headers:** `X-CSRFToken` (wymagany dla żądań z przeglądarki).

*   **Usuwanie lekcji:**
    *   **Endpoint:** `DELETE /api/courses/{course_id}/lessons/{lesson_id}/`
    *   **Response:** `204 No Content`.

## 8. Interakcje użytkownika
1.  **Wejście na stronę:** Pobranie listy lekcji dla kursu. Jeśli brak lekcji -> wyświetlenie komunikatu "Brak lekcji".
2.  **Kliknięcie "Dodaj lekcję":** Przekierowanie do formularza tworzenia nowej lekcji.
3.  **Przełączenie statusu (Toggle):**
    *   Użytkownik klika przełącznik.
    *   UI aktualizuje się natychmiast (Optimistic UI) zmieniając etykietę (np. na "Zapisywanie...").
    *   W tle leci żądanie `PATCH`.
    *   Sukces: Status zostaje potwierdzony.
    *   Błąd: UI cofa zmianę przełącznika i wyświetla "tost" z błędem.
4.  **Kliknięcie "Usuń":**
    *   Wyświetlenie systemowego `confirm()` lub modala: "Czy na pewno usunąć lekcję?".
    *   Potwierdzenie -> Żądanie `DELETE`.
    *   Sukces -> Wiersz znika z tabeli (animacja zanikania).

## 9. Warunki i walidacja
*   **Uprawnienia:** Tylko instruktor przypisany do kursu (lub Admin) może wyświetlić widok. Weryfikacja po stronie Django (`LoginRequiredMixin`, `UserPassesTestMixin`).
*   **Dostępność kursu:** Sprawdzenie czy `course_id` istnieje.
*   **CSRF:** Wszystkie żądania modyfikujące (PATCH, DELETE) muszą zawierać token CSRF.

## 10. Obsługa błędów
*   **Błąd 404 (Kurs nie istnieje):** Standardowa strona 404 Django.
*   **Błąd 403 (Brak uprawnień):** Przekierowanie do Dashboardu lub strona 403.
*   **Błąd API (Toggle/Delete):**
    *   Wyświetlenie powiadomienia (alert/toast) o niepowodzeniu.
    *   W przypadku Toggle: przywrócenie poprzedniego stanu przełącznika.

## 11. Kroki implementacji
1.  **Backend - View & QuerySet:**
    *   Utworzenie `CourseLessonsView` w `views.py`.
    *   Przygotowanie QuerySet: pobranie lekcji dla kursu z `annotate(files_count=Count('attachments'))`.
    *   Dodanie sprawdzenia uprawnień (czy user to instruktor kursu).
2.  **Backend - URL:**
    *   Rejestracja ścieżki w `urls.py`.
3.  **Frontend - Szablon:**
    *   Stworzenie pliku `templates/instructor/course_lessons.html`.
    *   Implementacja tabeli HTML iterującej po lekcjach.
4.  **Frontend - Interaktywność (Alpine.js):**
    *   Dodanie `x-data` do wierszy tabeli.
    *   Implementacja metod `toggleStatus` i `deleteLesson` wykorzystujących `fetch`.
    *   Obsługa tokena CSRF w nagłówkach żądań JS.
5.  **Style:**
    *   Ostylowanie tabeli i badge'y statusów (korzystając z klas CSS projektu).
6.  **Testy:**
    *   Weryfikacja wyświetlania dla instruktora i blokady dla studenta.
    *   Test manualny przełączania statusu i usuwania.

