# Plan implementacji widoku Lekcji dla Studenta

## 1. Przegląd
Widok ten umożliwia studentowi zapoznanie się z treścią pojedynczej lekcji w ramach kursu. Użytkownik może przeczytać opis lekcji oraz pobrać załączone materiały (pliki). Widok jest dostępny tylko dla studentów, którzy mają aktywny (zaakceptowany) zapis na dany kurs, a sama lekcja jest opublikowana.

## 2. Routing widoku
*   **Ścieżka URL:** `/student/courses/<int:course_id>/lessons/<int:lesson_id>/`
*   **Nazwa URL:** `student_lesson_detail`
*   **Widok Django:** `StudentLessonDetailView` (renderujący szablon `kursy/student/lesson_detail.html`)

## 3. Struktura komponentów
Widok zostanie zbudowany jako szablon Django wykorzystujący Alpine.js do pobrania i wyświetlenia szczegółowych danych z API.

Hierarchia:
*   `BaseTemplate` (layout, navbar)
    *   `LessonDetailContainer` (główny kontener, inicjalizacja Alpine.js)
        *   `Breadcrumbs` (nawigacja okruszkowa: Moje Kursy > Kurs > Lekcja)
        *   `LessonHeader` (Tytuł, data)
        *   `LessonContent` (Opis tekstowy)
        *   `AttachmentsSection` (Sekcja materiałów do pobrania)
            *   `AttachmentList`
                *   `AttachmentItem` (Ikona, nazwa, rozmiar, przycisk pobierania)

## 4. Szczegóły komponentów

### `LessonDetailContainer` (x-data="lessonDetail")
*   **Opis:** Komponent zarządzający stanem widoku, pobieraniem danych z API i obsługą błędów.
*   **Główne elementy:** `div` otaczający całą treść.
*   **Obsługiwane zdarzenia:** `init` (pobranie danych lekcji).
*   **Warunki walidacji:** Sprawdzenie, czy `course_id` i `lesson_id` są poprawnymi liczbami.
*   **Stan:** `isLoading`, `lesson`, `error`.

### `Breadcrumbs`
*   **Opis:** Statyczna lub dynamiczna nawigacja powrotna.
*   **Elementy:** Link do Dashboardu, Link do szczegółów kursu, Tytuł bieżącej lekcji (tekst).

### `AttachmentsSection`
*   **Opis:** Kontener wyświetlający listę załączników, jeśli istnieją.
*   **Elementy:** Nagłówek "Materiały do pobrania", lista `ul` lub `div` dla kafelków.
*   **Logika:** Ukryty, jeśli `lesson.attachments` jest puste.

### `AttachmentItem`
*   **Opis:** Pojedynczy element reprezentujący plik.
*   **Elementy:**
    *   Ikona zależna od typu pliku (PDF, ZIP, DOCX, inne).
    *   Nazwa pliku (`original_filename`).
    *   Przycisk/Link "Pobierz".
*   **Interakcje:** Kliknięcie w link pobierania (bezpośredni link do API endpointu pobierania lub obsługa przez `window.open`).

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

## 6. Zarządzanie stanem
Stan widoku jest zarządzany lokalnie przez komponent Alpine.js (`x-data="lessonDetail(courseId, lessonId)"`).
*   Dane lekcji są pobierane w hooku `init()`.
*   Token autoryzacji jest pobierany z `localStorage` (obsługa przez `ApiHandler` lub helper).

## 7. Integracja API

### Pobranie szczegółów lekcji
*   **Endpoint:** `GET /api/courses/{course_id}/lessons/{lesson_id}/`
*   **Wymagane nagłówki:** `Authorization: Bearer <token>`
*   **Odpowiedź sukcesu (200):** Obiekt JSON zgodny z `LessonDetailDTO`.
*   **Błędy:**
    *   `403 Forbidden`: Użytkownik nie jest zapisany na kurs lub lekcja nie jest opublikowana.
    *   `404 Not Found`: Lekcja nie istnieje.

### Pobieranie pliku
*   **Endpoint:** `GET /api/attachments/{attachment_id}/download/`
*   **Metoda:** GET (tradycyjny link `href` lub `window.open`, aby przeglądarka obsłużyła pobieranie pliku). Endpoint ten powinien zliczyć pobranie i zwrócić strumień pliku.
*   **Uwaga:** Jeśli endpoint wymaga tokena w nagłówku (Bearer), nie można użyć zwykłego linku `<a>`. W takim przypadku należy użyć `fetch` z `blob()` i utworzyć tymczasowy link URL (`URL.createObjectURL`), lub przekazać token w query param (jeśli API na to pozwala - mniej bezpieczne), lub użyć mechanizmu cookies sesyjnych (jeśli wdrożony). **Decyzja:** Zgodnie z planem API i architekturą ("Token JWT przechowywany w localStorage"), standardowe linki nie zadziałają dla chronionego endpointu bez cookies.
    *   *Rozwiązanie:* Funkcja `downloadFile(attachmentId)` w Alpine.js, która wykonuje `fetch` z nagłówkiem Auth, pobiera Bloba i wymusza pobranie w przeglądarce.

## 8. Interakcje użytkownika
1.  **Wejście na stronę:** Wyświetlenie szkieletu (loader).
2.  **Załadowanie danych:** Wyświetlenie tytułu, opisu i listy plików.
3.  **Kliknięcie "Pobierz" przy pliku:**
    *   Wywołanie funkcji pobierania.
    *   (Opcjonalnie) Zmiana stanu przycisku na "Pobieranie...".
    *   Rozpoczęcie pobierania pliku przez przeglądarkę.
4.  **Błąd ładowania:** Wyświetlenie komunikatu błędu i przycisku powrotu do kursu.

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

3.  **Logika Frontend (Alpine.js):**
    *   Zdefiniować komponent `lessonDetail`.
    *   Zaimplementować funkcję `init` pobierającą dane z `/api/courses/...`.
    *   Zaimplementować funkcję `downloadFile` obsługującą pobieranie z autoryzacją (Blob).
    *   Dodać logikę wyboru ikony na podstawie rozszerzenia pliku.

4.  **Testy Manualne:**
    *   Zalogować się jako Student przypisany do kursu -> wejść w lekcję -> sprawdzić dane i pobieranie.
    *   Zalogować się jako Student nieprzypisany -> sprawdzić brak dostępu.
    *   Sprawdzić lekcję nieopublikowaną (powinna być niedostępna).

