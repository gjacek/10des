# Plan implementacji widoku Moje Kursy (Dashboard Studenta)

## 1. Przegląd
Widok "Moje Kursy" (Dashboard Studenta) służy do wyświetlania listy kursów, na które zalogowany student jest zapisany i do których ma dostęp (status `approved`). Jest to główny punkt startowy dla studenta, pozwalający na szybkie przejście do treści edukacyjnych.

## 2. Routing widoku
*   **Ścieżka:** `/student/my-courses/`
*   **Nazwa URL (Django):** `student_my_courses`
*   **Plik widoku (Django):** `devs10/kursy/views.py` (lub `apps/student/views.py` w zależności od struktury)

## 3. Struktura komponentów
Widok zostanie zrealizowany w modelu hybrydowym: szablon Django (struktura) + Alpine.js (logika pobierania danych i stan).

*   `base.html` (Layout główny)
    *   `my_courses.html` (Główny szablon widoku)
        *   `Container` (Alpine `x-data="myCoursesData"`)
            *   `PageHeader` (Tytuł)
            *   `LoadingState` (Spinner/Skeleton)
            *   `ErrorState` (Komunikat błędu)
            *   `EmptyState` (Gdy brak kursów)
            *   `CourseGrid` (Siatka kart)
                *   `CourseCard` (Komponent karty kursu - pętla `x-for`)

## 4. Szczegóły komponentów

### `my_courses.html` (Główny Kontener)
*   **Opis:** Główny szablon renderowany przez Django. Inicjuje stan Alpine.js.
*   **Główne elementy:** `div` z atrybutem `x-data="myCoursesData()"`.
*   **Obsługiwane zdarzenia:** `x-init` (automatyczne pobranie kursów po załadowaniu).
*   **Walidacja:** Sprawdzenie tokena autoryzacji (w `ApiHandler`).

### `CourseCard` (Element listy)
*   **Opis:** Karta prezentująca pojedynczy kurs.
*   **Główne elementy:**
    *   Nazwa kursu (`h3`)
    *   Edycja (`badge`/`span`)
    *   Prowadzący (`p`)
    *   Przycisk "Przejdź do kursu" (Link `a`).
*   **Propsy (w kontekście Alpine):** Obiekt `course` przekazywany w pętli `x-for`.

### `EmptyState`
*   **Opis:** Komponent wyświetlany, gdy lista kursów jest pusta (i nie ma błędów/ładowania).
*   **Główne elementy:**
    *   Ikona/Ilustracja.
    *   Komunikat: "Nie jesteś zapisany na żaden kurs".
    *   Przycisk: "Zobacz dostępne kursy" (kierujący do `/student/courses/`).

## 5. Typy (DTO i ViewModel)

### `CourseViewModel`
Obiekt reprezentujący kurs na frontendzie (mapowany z odpowiedzi API).

```typescript
interface CourseViewModel {
    id: number;
    name: string;
    description: string;
    instructor: {
        id: number;
        first_name: string;
        last_name: string;
        email: string;
    };
    edition: {
        id: number;
        name: string;
    };
    // Opcjonalnie: progress, last_accessed (jeśli dostępne w API w przyszłości)
}
```

## 6. Zarządzanie stanem (Alpine.js)

Wykorzystany zostanie "custom logic" w postaci obiektu `Alpine.data`.

**Stan (`myCoursesData`):**
*   `courses`: `CourseViewModel[]` - lista pobranych kursów (inicjalnie pusta).
*   `isLoading`: `boolean` - flaga ładowania (inicjalnie `true`).
*   `error`: `string | null` - treść błędu w przypadku niepowodzenia.

## 7. Integracja API

**Endpoint:** `GET /api/users/me/enrollments/`
*Uwaga: W promptcie zasugerowano endpoint `/api/courses/` (katalog), jednak zgodnie z celem widoku ("kursy do których student ma dostęp") oraz `api-plan.md`, właściwym endpointem jest lista zapisów użytkownika.*

*   **Request:**
    *   Headers: `Authorization: Bearer <token>`
    *   Query Params: `status=approved` (aby pobrać tylko aktywne kursy).
*   **Response (JSON):**
    ```json
    [
      {
        "id": 1,
        "status": "approved",
        "course": {
             "id": 101,
             "name": "Analiza Danych",
             "edition": { "name": "2024/L" },
             "instructor": { "first_name": "Jan", "last_name": "Kowalski" }
        }
      }
    ]
    ```
    *(Struktura zostanie spłaszczona w JS do tablicy kursów).*

## 8. Interakcje użytkownika

1.  **Wejście na stronę:** Automatyczne pobranie listy kursów (`x-init`).
2.  **Kliknięcie w kurs:** Przekierowanie do widoku szczegółów kursu (`/student/courses/{id}/`).
3.  **Kliknięcie w "Zobacz dostępne kursy" (Empty State):** Przekierowanie do katalogu (`/student/courses/`).
4.  **Obsługa błędu:** Możliwość ponowienia próby (przycisk "Spróbuj ponownie" w stanie błędu).

## 9. Warunki i walidacja

*   **Dostęp:** Widok dostępny tylko dla zalogowanych użytkowników z rolą Student. (Weryfikowane przez Django View `LoginRequiredMixin` oraz API Permissions).
*   **Widoczność kursów:** Wyświetlane są tylko kursy ze statusem enrollmentu `approved`.

## 10. Obsługa błędów

*   **401 Unauthorized:** Przekierowanie do logowania (obsługiwane przez `ApiHandler`).
*   **Błąd sieci/API:** Ustawienie stanu `error` i wyświetlenie komunikatu "Nie udało się pobrać listy kursów" z przyciskiem retry.
*   **Pusta lista:** Wyświetlenie komponentu `EmptyState`.

## 11. Kroki implementacji

1.  **Backend (Django View):** Utworzenie widoku renderującego szablon (np. `StudentMyCoursesView` dziedziczący po `TemplateView`).
2.  **Routing (urls.py):** Rejestracja ścieżki `/student/my-courses/`.
3.  **Szablon (HTML):**
    *   Stworzenie pliku `my_courses.html` rozszerzającego `base.html`.
    *   Implementacja struktury HTML z klasami CSS (Pico.css).
4.  **Logika (JS/Alpine):**
    *   Stworzenie komponentu `myCoursesData` w pliku statycznym lub bloku `<script>`.
    *   Implementacja funkcji `fetchCourses` korzystającej z `ApiHandler` (lub `fetch`).
    *   Mapowanie odpowiedzi API na strukturę `courses`.
5.  **Integracja UI:**
    *   Podpięcie dyrektyw Alpine (`x-if`, `x-for`, `x-text`) do HTML.
    *   Obsługa stanów Loading/Empty/Error.
6.  **Weryfikacja:** Test manualny - zalogowanie jako student, sprawdzenie czy widoczne są tylko przypisane kursy.

