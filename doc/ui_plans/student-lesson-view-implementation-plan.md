# Plan implementacji widoku Lekcji dla Studenta

## 1. Przegląd
Widok ten umożliwia studentowi zapoznanie się z treścią pojedynczej lekcji w ramach kursu. Użytkownik może przeczytać opis lekcji oraz pobrać załączone materiały (pliki). Widok jest dostępny tylko dla studentów, którzy mają aktywny (zaakceptowany) zapis na dany kurs, a sama lekcja jest opublikowana.

## 2. Routing widoku
*   **Ścieżka URL:** `/student/courses/<int:course_id>/lessons/<int:lesson_id>/`
*   **Nazwa URL:** `student_lesson_detail`
*   **Widok Django:** `StudentLessonDetailView` (renderujący szablon `kursy/student/lesson_detail.html`)

## 3. Struktura komponentów
Widok zostanie zbudowany jako standardowy szablon Django (SSR). Alpine.js może być użyty do drobnych interakcji (np. zamykanie alertów), ale dane są renderowane przez serwer.

Hierarchia:
*   `BaseTemplate` (layout, navbar)
    *   `LessonDetailContainer` (główny kontener)
        *   `Breadcrumbs` (nawigacja okruszkowa)
        *   `LessonHeader` (Tytuł, data - tagi `{{ lesson.title }}`)
        *   `LessonContent` (Opis tekstowy - tag `{{ lesson.description }}`)
        *   `AttachmentsSection` (Sekcja materiałów do pobrania - pętla `{% for %}`)
            *   `AttachmentList`
                *   `AttachmentItem` (Ikona, nazwa, rozmiar, link pobierania)

## 4. Szczegóły komponentów

### `LessonDetailContainer`
*   **Opis:** Główny kontener wyświetlający treść lekcji.
*   **Dane (Context):** Obiekt `lesson` (z relacją `attachments`).

### `AttachmentsSection`
*   **Opis:** Kontener wyświetlający listę załączników.
*   **Warunki:** Wyświetlany tylko jeśli `lesson.attachments.exists()`.
*   **Elementy:** Pętla `{% for attachment in lesson.attachments.all %}`.

### `AttachmentItem`
*   **Opis:** Pojedynczy element reprezentujący plik.
*   **Elementy:**
    *   Nazwa pliku (`{{ attachment.original_filename }}`)
    *   Link "Pobierz" (`<a href="...">`) prowadzący do widoku pobierania.

## 5. Typy

### `LessonDetailDTO` (Model odpowiedzi z API)
```typescript
interface LessonDetailDTO {
    id: number;
    title: string;
    description: string;
    is_published: boolean;
    attachments: AttachmentDTO[]; // Zakładając zagnieżdżenie w odpowiedzi API
}
```

### `AttachmentDTO`
```typescript
interface AttachmentDTO {
    id: number;
    original_filename: string;
    file_url: string; // Signed URL lub link do endpointu download
    download_count: number;
}
```

### `ViewModel` (Stan w Alpine.js)
```javascript
{
    isLoading: boolean,
    error: string | null,
    lesson: {
        id: number | null,
        title: string,
        description: string,
        attachments: Array // lista AttachmentDTO
    } | null,
    courseId: number, // pobrane z URL lub wstrzyknięte przez Django
    lessonId: number  // pobrane z URL lub wstrzyknięte przez Django
}
```

## 6. Zarządzanie stanem (SSR)
Stan widoku jest w całości zarządzany przez serwer. Dane są pobierane w widoku Django i przekazywane do szablonu.

## 7. Integracja API

Widok lekcji nie korzysta z API do wyświetlania treści (SSR).

### Pobieranie pliku
*   **Endpoint:** `GET /api/attachments/{attachment_id}/download/`
*   **Metoda:** Standardowy link GET.
*   **Autoryzacja:** Cookie sesyjne. Widok Django sprawdza uprawnienia (czy student jest zapisany na kurs).
*   **Odpowiedź:** Strumień pliku (`FileResponse`) z nagłówkiem `Content-Disposition: attachment`.

## 8. Interakcje użytkownika
1.  **Wejście na stronę:** Serwer renderuje stronę z treścią lekcji.
2.  **Kliknięcie "Pobierz" przy pliku:** Przeglądarka rozpoczyna pobieranie pliku.
3.  **Błąd dostępu:** Jeśli użytkownik nie ma uprawnień, widzi stronę błędu 403.

## 9. Warunki i walidacja
*   **Uprawnienia:** Frontend polega na walidacji API (kod 403). Jeśli API zwróci 403, wyświetlany jest komunikat "Brak dostępu do tej lekcji".
*   **Publikacja:** Jeśli lekcja nie jest opublikowana, API nie zwróci jej dla studenta (403/404), co zostanie obsłużone jako błąd dostępu/brak zasobu.
*   **Dane:** Jeśli lista załączników jest pusta, sekcja "Materiały" nie jest renderowana.

## 10. Obsługa błędów
*   **Brak autoryzacji (401):** Przekierowanie do strony logowania.
*   **Brak dostępu (403):** Komunikat "Nie masz uprawnień do wyświetlenia tej lekcji" + link powrotu do listy kursów.
*   **Nie znaleziono (404):** Komunikat "Lekcja nie istnieje".
*   **Błąd serwera (500) / Sieci:** Ogólny komunikat "Wystąpił błąd podczas ładowania lekcji. Spróbuj ponownie później."

## 11. Kroki implementacji

1.  **Backend (Django View & URL):**
    *   Dodać wpis w `kursy/urls.py` dla ścieżki `/student/courses/<int:course_id>/lessons/<int:lesson_id>/`.
    *   Utworzyć prosty widok `StudentLessonDetailView` w `kursy/views.py`, który renderuje szablon `kursy/student/lesson_detail.html`. Można tu wstępnie sprawdzić uprawnienia (np. `LoginRequiredMixin`), aby zredukować ruch, ale główna logika danych jest w API.

2.  **Szablon (HTML):**
    *   Utworzyć plik `kursy/templates/kursy/student/lesson_detail.html` dziedziczący po `base.html`.
    *   Zaimplementować strukturę HTML z klasami Pico.css.

3.  **Logika Frontend (Minimalna):**
    *   Opcjonalnie Alpine.js do drobnych interakcji (np. potwierdzenia).
    *   Główna logika (renderowanie) w szablonie Django.

4.  **Testy Manualne:**
    *   Zalogować się jako Student przypisany do kursu -> wejść w lekcję -> sprawdzić dane i pobieranie.
    *   Zalogować się jako Student nieprzypisany -> sprawdzić brak dostępu.
    *   Sprawdzić lekcję nieopublikowaną (powinna być niedostępna).

