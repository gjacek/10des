# Plan implementacji widoku Edycji Lekcji i Plików

## 1. Przegląd
Widok ten umożliwia Prowadzącemu edycję szczegółów istniejącej lekcji (tytuł, opis, status publikacji) oraz zarządzanie powiązanymi plikami (dodawanie, usuwanie). Strona łączy tradycyjny formularz Django do edycji danych lekcji z interaktywnym komponentem opartym na Alpine.js do asynchronicznego zarządzania załącznikami bez przeładowania strony.

## 2. Routing widoku
*   **Ścieżka:** `/instructor/courses/<int:course_id>/lessons/<int:lesson_id>/edit/`
*   **Nazwa URL:** `instructor_lesson_edit`
*   **Wymagane uprawnienia:** Zalogowany użytkownik, Rola Prowadzącego, Właściciel kursu.

## 3. Struktura komponentów
Strona oparta jest na szablonie Django (`base.html`) i dzieli się na dwie główne sekcje logiczne:

1.  **Formularz Lekcji (Server-Side):** Standardowy formularz Django renderowany w szablonie, obsługiwany przez żądanie POST (synchroniczne).
2.  **Menedżer Załączników (Client-Side - Alpine.js):** Sekcja interaktywna, komunikująca się z REST API w celu dodawania i usuwania plików.

**Drzewo komponentów (HTML/Alpine):**
```
[Main Container]
  ├── [Breadcrumbs] (Kursy > Kurs X > Lekcja Y > Edycja)
  ├── [Card - Dane Lekcji]
  │     └── <form method="POST"> (Django Form)
  │           ├── CSRF Token
  │           ├── Input: Tytuł
  │           ├── Textarea: Opis
  │           ├── Checkbox: Opublikowana (Switch)
  │           └── Button: Zapisz zmiany
  └── [Card - Materiały] (x-data="attachmentsManager")
        ├── [List] Lista załączników
        │     └── [Item] Nazwa pliku | Ilość pobrań | Przycisk Usuń
        ├── [Error Alert] Komunikaty błędów walidacji
        └── [Upload Control]
              ├── Input File (multiple)
              └── Button: Dodaj pliki
```

## 4. Szczegóły komponentów

### Formularz Lekcji (Django)
*   **Opis:** Standardowy formularz `ModelForm` dla modelu `Lesson`.
*   **Główne elementy:** Pola formularza renderowane za pomocą `django-widget-tweaks` lub ręcznie, stylizowane zgodnie z `pico.css`.
*   **Obsługiwane interakcje:** Edycja tekstu, przełączanie checkboxa, submit formularza (przeładowanie strony).
*   **Walidacja:** Server-side (wymagane pola).
*   **Propsy (Context):** `form` (instancja `LessonForm`), `lesson` (obiekt lekcji), `course` (obiekt kursu).

### Menedżer Załączników (Alpine.js)
*   **Opis:** Komponent zarządzający listą plików za pomocą API.
*   **Główne elementy:**
    *   Lista `<ul>` renderowana dyrektywą `x-for`.
    *   Input `<input type="file" multiple>` obsługiwany przez `x-ref`.
*   **Stan (x-data):**
    *   `attachments`: Tablica obiektów plików.
    *   `isLoading`: Boolean (blokada UI podczas operacji).
    *   `error`: String (komunikat błędu).
*   **Obsługiwane interakcje:**
    *   `init()`: Pobranie listy załączników przy załadowaniu.
    *   `uploadFiles()`: Wybranie plików, walidacja wstępna, wysyłka do API.
    *   `deleteAttachment(id)`: Żądanie usunięcia pliku.
*   **Warunki walidacji (Client-side):**
    *   Limit plików: Max 10 łącznie (obecne + nowe).
    *   Rozmiar pliku: Max 10MB na plik.
    *   Rozszerzenia: Whitelist (pdf, zip, pptx, docx, txt, jpg, jpeg).

## 5. Typy

### Django Context (Template)
*   `course`: Obiekt `Course`.
*   `lesson`: Obiekt `Lesson`.
*   `form`: Obiekt `LessonForm`.

### JavaScript (Alpine.js Data)
```javascript
// Attachment DTO (z API)
interface Attachment {
    id: number;
    original_filename: string;
    download_count: number;
    file_url: string;
}

// Alpine Component Data
interface AttachmentsManagerState {
    courseId: number;
    lessonId: number;
    attachments: Attachment[];
    isLoading: boolean;
    error: string | null;
    
    // Metody
    fetchAttachments(): Promise<void>;
    uploadFiles(): Promise<void>;
    deleteAttachment(id: number): Promise<void>;
}
```

## 6. Zarządzanie stanem
Stan danych lekcji jest zarządzany przez Django (Request/Response cycle).
Stan załączników jest lokalny dla widoku i zarządzany przez Alpine.js (`x-data`).
Dane inicjalne (np. ID kursu i lekcji) przekazywane są z szablonu Django do Alpine za pomocą atrybutów `data-*` lub filtru `json_script`.

## 7. Integracja API
Sekcja załączników komunikuje się z następującymi endpointami (zdefiniowanymi w `api-plan.md`):

1.  **Pobranie listy:** `GET /api/courses/{course_id}/lessons/{lesson_id}/attachments/`
2.  **Dodanie pliku:** `POST /api/courses/{course_id}/lessons/{lesson_id}/attachments/`
    *   Typ: `multipart/form-data`
    *   Parametr: `file`
3.  **Usunięcie pliku:** `DELETE /api/courses/{course_id}/lessons/{lesson_id}/attachments/{id}/`

**Autoryzacja:** Wszystkie żądania fetch muszą zawierać nagłówek `X-CSRFToken` (pobrany z ciasteczka `csrftoken`), ponieważ używamy sesji Django w przeglądarce.

## 8. Interakcje użytkownika
1.  **Edycja treści:** Użytkownik zmienia tytuł/opis i klika "Zapisz". Strona przeładowuje się z komunikatem sukcesu (Django Messages).
2.  **Dodawanie plików:**
    *   Użytkownik klika "Wybierz pliki" (input file).
    *   Wybiera jeden lub więcej plików.
    *   Klika "Wyślij".
    *   System sprawdza limity (rozmiar, ilość). Jeśli błąd -> wyświetla komunikat.
    *   Jeśli OK -> pokazuje stan ładowania, wysyła pliki jeden po drugim (lub równolegle).
    *   Po sukcesie -> lista odświeża się, input czyści.
3.  **Usuwanie plików:**
    *   Użytkownik klika ikonę "Usuń" przy pliku.
    *   System pyta o potwierdzenie (opcjonalnie `confirm()`).
    *   Wysyła żądanie DELETE.
    *   Usuwa element z listy w UI.

## 9. Warunki i walidacja

### Walidacja formularza lekcji (Django)
*   **Tytuł:** Wymagany, max długość (z modelu).
*   **Opis:** Wymagany.

### Walidacja załączników (Backend - Security)
*   **Wymuszona po stronie serwera:** API musi odrzucić żądanie, jeśli plik przekracza limity lub ma niedozwolone rozszerzenie (zgodnie z US-026 i US-010). Frontendowa walidacja jest tylko udogodnieniem UX.

### Walidacja załączników (JS/Alpine - UX)
*   **Ilość:** `attachments.length + newFiles.length <= 10`. Komunikat: "Maksymalnie 10 plików w lekcji."
*   **Rozmiar:** `file.size <= 10 * 1024 * 1024` (10MB). Komunikat: "Plik X jest za duży (max 10MB)."
*   **Typ:** Sprawdzenie rozszerzenia pliku względem białej listy: `.pdf, .zip, .pptx, .docx, .txt, .jpg, .jpeg`. Komunikat: "Niedozwolony format pliku X."

## 10. Obsługa błędów
*   **Błędy formularza (Django):** Wyświetlane nad polami formularza (standard Django).
*   **Błędy API (JS):**
    *   Przechwytywane w `catch` bloku `fetch`.
    *   Status 4xx/5xx parsowany i wyświetlany w zmiennej `error` (widoczny alert w UI).
    *   Błędy sieciowe: Komunikat ogólny "Wystąpił błąd połączenia."

## 11. Kroki implementacji

1.  **Backend - Formularz:**
    *   Utworzyć `LessonUpdateForm` w `forms.py` (dziedziczący po `ModelForm`).
2.  **Backend - Widok:**
    *   Utworzyć widok `LessonUpdateView` w `views.py` (używając `UpdateView` lub FBV).
    *   Zapewnić sprawdzanie uprawnień (decorator `user_is_instructor`, `user_owns_course`).
    *   Dodać obsługę kontekstu dla szablonu.
3.  **Szablon:**
    *   Utworzyć plik `kursy/templates/kursy/instructor/lesson_edit.html`.
    *   Rozszerzyć `base.html`.
    *   Zaimplementować formularz edycji lekcji.
4.  **Frontend - Alpine Component:**
    *   Dodać skrypt Alpine.js w sekcji załączników.
    *   Zaimplementować logikę `fetchAttachments`, `upload`, `delete`.
    *   Zaimplementować walidację JS.
5.  **Routing:**
    *   Dodać ścieżkę w `kursy/urls.py`.

