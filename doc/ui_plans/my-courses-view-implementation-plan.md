# Plan implementacji widoku Moje Kursy (Dashboard Studenta)

## 1. Przegląd
Widok "Moje Kursy" (Dashboard Studenta) służy do wyświetlania listy kursów, na które zalogowany student jest zapisany i do których ma dostęp (status `approved`). Jest to główny punkt startowy dla studenta, pozwalający na szybkie przejście do treści edukacyjnych.

## 2. Routing widoku
*   **Ścieżka:** `/student/my-courses/`
*   **Nazwa URL (Django):** `student_my_courses`
*   **Plik widoku (Django):** `devs10/kursy/views.py` (lub `apps/student/views.py` w zależności od struktury)

## 3. Struktura komponentów
Widok oparty na standardowym szablonie Django (Server-Side Rendering). Alpine.js może być użyty opcjonalnie do drobnych interakcji UI, ale główne dane są renderowane przez serwer.

*   `base.html` (Layout główny)
    *   `my_courses.html` (Główny szablon widoku)
        *   `PageHeader` (Tytuł)
        *   `EmptyState` (Warunek `{% if not courses %}`)
        *   `CourseGrid` (Siatka kart - pętla `{% for %}`)
            *   `CourseCard` (Komponent karty kursu)

## 4. Szczegóły komponentów

### `my_courses.html` (Główny Kontener)
*   **Opis:** Główny szablon renderowany przez Django.
*   **Dane (Context):** Lista obiektów `courses` przekazana z widoku.

### `CourseCard` (Element listy)
*   **Opis:** Karta prezentująca pojedynczy kurs.
*   **Główne elementy:**
    *   Nazwa kursu (`{{ course.name }}`)
    *   Edycja (`{{ course.edition.name }}`)
    *   Prowadzący (`{{ course.instructor.get_full_name }}`)
    *   Przycisk "Przejdź do kursu" (Link `{% url ... %}`).

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

## 6. Zarządzanie stanem (Django)

Stan widoku jest zarządzany po stronie serwera.
*   **Pobieranie danych:** Widok Django pobiera listę kursów powiązanych z zalogowanym użytkownikiem (status `approved`).
*   **Renderowanie:** Szablon otrzymuje gotową listę.

## 7. Integracja API

Widok nie korzysta z REST API do pobierania listy kursów (SSR).
Dane są pobierane bezpośrednio z bazy danych w widoku.

**Zapytanie (ORM):**
`Enrollment.objects.filter(student=request.user, status='approved').select_related('course', 'course__edition', 'course__instructor')`

## 8. Interakcje użytkownika

1.  **Wejście na stronę:** Serwer renderuje stronę z listą kursów.
2.  **Kliknięcie w kurs:** Przekierowanie do widoku szczegółów kursu (`/student/courses/{id}/`).
3.  **Kliknięcie w "Zobacz dostępne kursy" (Empty State):** Przekierowanie do katalogu (`/student/courses/`).

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

