# Plan implementacji widoku Szczegóły Kursu (Student)

## 1. Przegląd
Widok szczegółowy kursu przeznaczony dla studenta. Pozwala zapoznać się z informacjami o kursie oraz uzyskać dostęp do listy opublikowanych lekcji. Widok jest dostępny wyłącznie dla studentów posiadających aktywny (zatwierdzony) zapis na dany kurs.

## 2. Routing widoku
*   **Ścieżka URL:** `/student/courses/<int:pk>/`
*   **Nazwa URL (Django):** `student:course_detail`
*   **Widok (Class Based View):** `StudentCourseDetailView`

## 3. Struktura komponentów
Widok zostanie zrealizowany jako szablon Django (`course_detail.html`) renderowany po stronie serwera, wykorzystujący system dziedziczenia szablonów (`base.html`).

**Hierarchia:**
*   `BaseLayout` (Główny layout aplikacji)
    *   `CourseDetailView` (Główny kontener widoku)
        *   `CourseHeader` (Sekcja nagłówka kursu)
            *   `InstructorInfo` (Informacje o prowadzącym)
        *   `LessonList` (Lista lekcji)
            *   `LessonItem` (Pojedynczy element listy lekcji - link)
            *   `EmptyState` (Komunikat w przypadku braku lekcji)

## 4. Szczegóły komponentów

### 1. CourseHeader (Szablon/Partial)
*   **Opis:** Wyświetla kluczowe metadane kursu.
*   **Główne elementy HTML:** `<h1>` (Nazwa), `<p>` (Opis), Badge (Edycja).
*   **Dane (Context):** Obiekt `course`.
*   **Wyświetlane pola:** `course.name`, `course.description`, `course.edition`.

### 2. InstructorInfo (Szablon/Partial)
*   **Opis:** Sekcja informacyjna o prowadzącym.
*   **Główne elementy HTML:** Avatar (opcjonalnie), Imię i Nazwisko, Link mailowy.
*   **Dane (Context):** `course.instructor`.
*   **Wyświetlane pola:** `instructor.first_name`, `instructor.last_name`, `instructor.email`.

### 3. LessonList (Szablon/Partial)
*   **Opis:** Lista iterująca po dostępnych lekcjach.
*   **Główne elementy HTML:** `<ul>` lub `div.list-group`.
*   **Obsługiwane warunki:** Sprawdzenie czy lista `lessons` nie jest pusta. Jeśli pusta -> renderuj `EmptyState`.
*   **Dane (Context):** QuerySet `lessons`.

### 4. LessonItem (Szablon/Partial)
*   **Opis:** Klikalny element listy przenoszący do szczegółów lekcji.
*   **Główne elementy HTML:** `<a>` (Link), `<span>` (Tytuł), Ikona statusu (Opublikowana - choć student widzi tylko takie).
*   **Props/Context:** Obiekt `lesson`.
*   **Interakcja:** Kliknięcie przekierowuje do `student:lesson_detail` (`/student/courses/<course_id>/lessons/<lesson_id>/`).

## 5. Typy i Modele danych
W kontekście Django Templates operujemy na instancjach modeli (ORM).

### Wymagane pola w Context:
1.  **`course` (Model: Course)**
    *   `id`: `int` (do linkowania)
    *   `name`: `str`
    *   `description`: `str`
    *   `edition`: `str` (z powiązanego modelu `CourseEdition`)
    *   `instructor`: `User` (FK)

2.  **`lessons` (QuerySet: Lesson)**
    *   Lista obiektów posortowana alfabetycznie po tytule.
    *   Filtrowanie: `is_published=True`.
    *   Pola obiektu:
        *   `id`: `int`
        *   `title`: `str`
        *   *(Opcjonalnie)* `description`: `str` (krótki opis, jeśli wymagany na liście)

## 6. Zarządzanie stanem
Stan widoku jest zarządzany całkowicie po stronie serwera (Server-Side Rendering).
*   **Inicjalizacja:** Dane są pobierane w metodzie `get_context_data` widoku Django.
*   **Cache:** Opcjonalne cache'owanie fragmentów szablonu dla statycznych opisów kursów.

## 7. Integracja API / Backend
Widok nie korzysta z REST API (AJAX) do pobierania głównych danych, lecz z bezpośrednich zapytań ORM w widoku Django.

**Zapytania DB (Pseudokod):**
1.  **Pobranie kursu:**
    ```python
    course = get_object_or_404(Course, pk=self.kwargs['pk'])
    ```
2.  **Weryfikacja dostępu (Security):**
    ```python
    is_enrolled = Enrollment.objects.filter(
        student=request.user, 
        course=course, 
        status='approved'
    ).exists()
    if not is_enrolled: raise PermissionDenied
    ```
3.  **Pobranie lekcji (US-019, US-025):**
    ```python
    lessons = course.lessons.filter(is_published=True).order_by('title')
    ```

## 8. Interakcje użytkownika
*   **Wejście na stronę:** Automatyczne załadowanie danych kursu.
*   **Kliknięcie w lekcję:** Przejście do widoku szczegółów lekcji (`LessonDetailView`).
*   **Powrót:** Przycisk "Wróć do listy kursów" kierujący do `/student/my-courses/`.

## 9. Warunki i walidacja
*   **Walidacja uwierzytelnienia:** Użytkownik musi być zalogowany (`LoginRequiredMixin`).
*   **Walidacja uprawnień (US-021):**
    *   Użytkownik musi być w grupie/roli Student.
    *   Użytkownik musi mieć rekord `Enrollment` dla tego kursu ze statusem `approved`.
*   **Walidacja danych:**
    *   Jeśli kurs nie istnieje -> 404.
    *   Jeśli kurs jest ukryty (`is_visible=False`) -> 404 Not Found (zgodnie z US-024, kurs znika z widoków studenta, nawet jeśli jest zapisany). To zapobiega domyślaniu się istnienia ukrytych zasobów.

## 10. Obsługa błędów
*   **404 Not Found:** Gdy `id` kursu jest nieprawidłowe.
*   **403 Forbidden:**
    *   Gdy użytkownik nie jest zapisany (brak `Enrollment`).
    *   Gdy status zapisu to `pending` lub `rejected`.
    *   Gdy kurs ma status `is_visible=False` (zgodnie z US-024).
*   **Pusta lista lekcji:** Wyświetlenie przyjaznego komunikatu "Brak opublikowanych lekcji w tym kursie".

## 11. Kroki implementacji
1.  **Backend (View):**
    *   Utworzyć klasę `StudentCourseDetailView` dziedziczącą po `LoginRequiredMixin` i `DetailView`.
    *   Zaimplementować metodę `get_queryset` lub `get_object` z uwzględnieniem `select_related` (instructor, edition) dla optymalizacji.
    *   Dodać logikę sprawdzania uprawnień (custom Mixin lub `dispatch` override): sprawdzenie `Enrollment` (status `approved`) oraz `Course.is_visible`.
    *   Nadpisać `get_context_data` aby pobrać `lessons` (`filter(is_published=True).order_by('title')`).

2.  **Frontend (Template):**
    *   Stworzyć plik `student/course_detail.html`.
    *   Zaimplementować dziedziczenie z `base.html`.
    *   Stworzyć sekcję nagłówka z danymi kursu.
    *   Stworzyć pętlę `{% for lesson in lessons %}` generującą listę linków.
    *   Dodać obsługę `{% empty %}` dla braku lekcji.

3.  **Routing (URLs):**
    *   Dodać ścieżkę w `student/urls.py`.

4.  **Testy:**
    *   Test dostępu dla niezalogowanego (redirect).
    *   Test dostępu dla niezapisanego studenta (403).
    *   Test dostępu dla zapisanego studenta (200, widoczność lekcji).
    *   Test widoczności nieopublikowanych lekcji (nie powinny być widoczne).
    *   Test kolejności sortowania lekcji (alfabetycznie).

