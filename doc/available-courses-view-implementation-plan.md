# Plan implementacji widoku Dostępne Kursy (Katalog)

## 1. Przegląd
Widok "Dostępne Kursy" jest przeznaczony dla Studentów. Prezentuje on listę wszystkich kursów w systemie, które mają status "Widoczny". Umożliwia Studentom przeglądanie oferty oraz wysyłanie próśb o dołączenie do kursów (zapisy). Widok informuje również o aktualnym statusie relacji studenta z kursem (np. czy prośba jest oczekująca lub odrzucona).

## 2. Routing widoku
*   **URL**: `/student/courses/`
*   **Nazwa URL**: `student_available_courses`
*   **Widok Django**: `StudentAvailableCoursesView`

## 3. Struktura komponentów
Widok oparty jest na szablonach Django (Server-Side Rendering) z interaktywnymi elementami obsługiwanymi przez Alpine.js.

*   **Layout Główny** (`base.html` - istniejący)
    *   **Kontener Widoku** (`courses/student/available_courses.html`)
        *   **Nagłówek Strony** (Tytuł: "Dostępne Kursy")
        *   **Lista Kursów** (`<ul>` / Grid)
            *   **Karta Kursu** (`<li>` / Card) - powielana dla każdego kursu
                *   **Informacje o Kursie** (Nazwa, Edycja, Prowadzący, Opis)
                *   **Panel Akcji** (Komponent Alpine.js `enrollmentAction`)
                    *   Przycisk "Wyślij prośbę" / Etykieta statusu

## 4. Szczegóły komponentów

### StudentAvailableCoursesView (Django View)
*   **Opis**: Widok klasy (Class-Based View), dziedziczący po `LoginRequiredMixin` i `TemplateView`. Odpowiada za pobranie danych i wyrenderowanie szablonu.
*   **Logika biznesowa**:
    1.  Pobiera wszystkie kursy z flagą `is_visible=True`.
    2.  Pobiera wszystkie zapisy (`Enrollment`) aktualnie zalogowanego studenta.
    3.  Tworzy strukturę danych, która dla każdego kursu zawiera informację o statusie zapisu studenta (Brak, Oczekujący, Zapisany, Odrzucony).
*   **Kontekst szablonu**:
    *   `courses_with_status`: Lista obiektów (słowników lub DTO) zawierających dane kursu oraz pole `user_status`.

### Template: courses/student/available_courses.html
*   **Opis**: Szablon HTML renderujący listę.
*   **Główne elementy**:
    *   Pętla `{% for item in courses_with_status %}`.
    *   Wyświetlanie danych: `item.course.name`, `item.course.description`, `item.course.instructor` itp.
    *   Inicjalizacja komponentu Alpine: `<div x-data="enrollmentAction({{ item.course.id }}, '{{ item.user_status }}')">`.

### Component Alpine: enrollmentAction
*   **Opis**: Komponent JavaScript (Alpine.js) zarządzający przyciskiem zapisu.
*   **Propsy (przekazywane przy inicjalizacji)**:
    *   `courseId`: ID kursu (Int).
    *   `initialStatus`: Status początkowy ('none', 'pending', 'approved', 'rejected').
*   **Stan (Data)**:
    *   `status`: Aktualny status (inicjowany z `initialStatus`).
    *   `isLoading`: Flaga boolean dla stanu ładowania przycisku.
*   **Obsługiwane zdarzenia**:
    *   `click` na przycisk "Wyślij prośbę": Uruchamia metodę `enroll()`.
*   **Metody**:
    *   `enroll()`: Wysyła żądanie `POST` do API `/api/courses/{id}/enroll/`.
*   **Warunki walidacji (UI)**:
    *   Jeśli `status == 'pending'`, przycisk zablokowany (napis "Oczekuje").
    *   Jeśli `status == 'approved'`, przycisk zablokowany lub link do kursu (napis "Zapisany").
    *   Jeśli `status == 'rejected'`, przycisk zablokowany (napis "Odrzucony").
    *   Jeśli `status == 'none'`, przycisk aktywny (napis "Wyślij prośbę").

## 5. Typy

### Django Context (CourseWithStatus)
Nie jest to formalny typ w TypeScript, ale struktura w Pythonie przekazywana do szablonu:
```python
class CourseWithStatus:
    course: Course
    user_status: str # 'none', 'pending', 'approved', 'rejected'
```

### Alpine Component State
*   `courseId`: Number
*   `status`: String ('none' | 'pending' | 'approved' | 'rejected')
*   `isLoading`: Boolean

## 6. Zarządzanie stanem
*   **Stan początkowy**: Dostarczany przez serwer (Django) w momencie renderowania strony. Jest to "pojedyncze źródło prawdy" w momencie ładowania.
*   **Stan lokalny**: Zarządzany przez Alpine.js po załadowaniu strony. Zmiana statusu po wysłaniu prośby następuje optymistycznie lub natychmiast po otrzymaniu odpowiedzi sukcesu z API.

## 7. Integracja API
Komponent Alpine.js będzie komunikował się z backendem używając `fetch`.

*   **Endpoint**: `POST /api/courses/{course_id}/enroll/`
*   **Nagłówki**:
    *   `Content-Type`: `application/json`
    *   `X-CSRFToken`: Token CSRF (wymagany przez Django). Należy go pobrać z `document.cookie` lub wyrenderować w szablonie jako zmienną globalną/wartość inputa.
*   **Body**: Puste (lub `{}`).
*   **Odpowiedź sukcesu (201)**:
    ```json
    {
      "message": "Enrollment request sent.",
      "status": "pending"
    }
    ```
*   **Odpowiedź błędu (400/403)**: Komunikat błędu (np. użytkownik już zapisany).

## 8. Interakcje użytkownika
1.  **Wejście na stronę**: Student widzi listę kursów. Przy kursach, do których nie należy, widzi przycisk "Wyślij prośbę".
2.  **Kliknięcie "Wyślij prośbę"**:
    *   Przycisk zmienia stan na "Ładowanie..." (spinner/disabled).
    *   Wysyłane jest żądanie do API.
3.  **Sukces zapisu**:
    *   Przycisk zmienia się na "Oczekuje" (disabled).
    *   Kolor przycisku/badge'a zmienia się na informacyjny (np. żółty/szary).
4.  **Próba zapisu na kurs odrzucony**:
    *   Przycisk jest od razu nieaktywny z napisem "Odrzucony" (na podstawie danych z serwera).

## 9. Warunki i walidacja
*   **Backend (API)**: Sprawdza, czy użytkownik nie jest już zapisany lub odrzucony. Sprawdza, czy kurs jest widoczny.
*   **Backend (View)**: Filtruje listę kursów tylko do `is_visible=True`.
*   **Frontend (Alpine)**: Blokuje interakcję dla statusów innych niż `none`.

## 10. Obsługa błędów
*   **Błąd API (np. 500)**: Wyświetlenie prostego `alert()` lub komunikatu toast z informacją "Wystąpił błąd, spróbuj ponownie". Stan przycisku wraca do aktywnego.
*   **Błąd walidacji (400)**: Jeśli API zwróci, że użytkownik już jest zapisany (np. w innej karcie), Alpine zaktualizuje status na otrzymany z serwera (jeśli API to zwróci) lub wyświetli komunikat o błędzie.

## 11. Kroki implementacji
1.  **Backend - View**:
    *   Utworzyć widok `StudentAvailableCoursesView` w aplikacji `courses`.
    *   Zaimplementować logikę pobierania `Course` i `Enrollment`.
    *   Zaimplementować logikę łączenia danych (kurs + status).
2.  **Backend - Template**:
    *   Stworzyć plik `courses/student/available_courses.html` (lub podobna ścieżka).
    *   Zaimplementować pętlę wyświetlającą karty kursów z użyciem stylów Pico.css.
3.  **Frontend - Alpine**:
    *   Zaimplementować komponent `enrollmentAction`.
    *   Dodać logikę pobierania CSRF tokena (np. funkcja pomocnicza `getCookie('csrftoken')`).
4.  **Routing**:
    *   Dodać ścieżkę `/student/courses/` w `courses/urls.py` (lub głównym `urls.py`).
5.  **Testowanie**:
    *   Zweryfikować poprawność wyświetlania statusów dla różnych scenariuszy (nowy, oczekujący, odrzucony).
    *   Sprawdzić działanie przycisku zapisu.

