# Plan implementacji widoku Kreator / Edycja Kursu

## 1. Przegląd
Widok ten umożliwia Prowadzącym tworzenie nowych kursów oraz edycję metadanych kursów istniejących. Jest to kluczowy element panelu instruktora, pozwalający na zarządzanie nazwą, opisem, przypisaną edycją (np. semestrem) oraz widocznością kursu. Widok oparty jest na szablonach Django z wykorzystaniem Alpine.js do obsługi formularza i komunikacji z API.

## 2. Routing widoku
*   **Tworzenie kursu:**
    *   URL: `/instructor/courses/create/`
    *   Nazwa widoku: `course_create`
*   **Edycja kursu:**
    *   URL: `/instructor/courses/<int:id>/edit/`
    *   Nazwa widoku: `course_edit`

## 3. Struktura komponentów
Widok wykorzystuje główny layout aplikacji i wstrzykuje do niego formularz zarządzany przez Alpine.js.

```text
BaseTemplate (base.html)
└── MainContainer (<main class="container">)
    └── PageHeader (hgroup)
        └── Title (Tworzenie kursu / Edycja kursu: [Nazwa])
    └── CourseFormContainer (article)
        └── Form (form x-data="courseForm")
            ├── GlobalErrors (div x-show="errors.non_field_errors")
            ├── NameField (input type="text")
            ├── EditionField (select)
            ├── DescriptionField (textarea)
            ├── VisibilitySwitch (input type="checkbox" role="switch")
            └── Actions (div class="grid")
                ├── CancelButton (a href="/instructor/dashboard/")
                └── SubmitButton (button type="submit")
```

## 4. Szczegóły komponentów

### `CourseForm` (Komponent Alpine.js)
*   **Opis:** Główny komponent obsługujący logikę formularza, walidację po stronie klienta oraz wysyłanie danych do API.
*   **Główne elementy HTML:**
    *   `<form>`: Główny kontener z obsługą `@submit.prevent="submit"`.
    *   `<input name="name">`: Pole tekstowe tytułu kursu.
    *   `<select name="edition">`: Lista rozwijana dostępnych edycji kursów.
    *   `<textarea name="description">`: Pole opisu (Markdown lub zwykły tekst).
    *   `<input type="checkbox" name="is_visible">`: Przełącznik widoczności kursu.
*   **Obsługiwane zdarzenia:**
    *   `submit`: Walidacja danych i wysłanie żądania do API (POST lub PUT).
    *   `input`: Czyszczenie błędów walidacji dla konkretnego pola.
*   **Obsługiwana walidacja:**
    *   **Nazwa (name):** Wymagane, niepuste.
    *   **Edycja (edition_id):** Wymagane, musi być wybrane z listy.
    *   **Opis (description):** Wymagane (zgodnie z PRD i API).
*   **Typy (Alpine Data):**
    *   `formData`: Obiekt przechowujący dane kursu (`name`, `description`, `edition_id`, `is_visible`).
    *   `isEditing`: Boolean, określa tryb (tworzenie vs edycja).
    *   `courseId`: ID edytowanego kursu (lub null).
    *   `isSaving`: Boolean, status wysyłania.
    *   `errors`: Obiekt błędów z API.
*   **Propsy (przekazywane z Django):**
    *   `editions`: Lista dostępnych edycji `[{id, name}, ...]`.
    *   `initialData`: Dane kursu przy edycji (lub pusty obiekt przy tworzeniu).

## 5. Typy

### DTO (Data Transfer Objects)

**CoursePayload (Request):**
```json
{
  "name": "string",
  "description": "string",
  "edition_id": "integer",
  "is_visible": "boolean"
}
```

**CourseResponse (Response):**
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "is_visible": "boolean",
  "edition": {
    "id": "integer",
    "name": "string"
  },
  "instructor": {
      "id": "integer",
      "email": "string"
  }
}
```

**ValidationError (Response 400):**
```json
{
  "name": ["To pole jest wymagane."],
  "edition_id": ["Nieprawidłowe ID edycji."]
}
```

## 6. Zarządzanie stanem
Stan formularza jest lokalny dla komponentu Alpine.js.
*   **Inicjalizacja:** Przy załadowaniu strony, Django wstrzykuje `initialData` (dla edycji) oraz `editions` bezpośrednio do `x-data`.
*   **Reaktywność:** Zmiany w polach input aktualizują model `formData`.
*   **Błędy:** Błędy walidacji z API są mapowane do obiektu `errors` i wyświetlane pod odpowiednimi polami.

```javascript
function courseForm(initialData, editions) {
    return {
        formData: {
            name: initialData?.name || '',
            description: initialData?.description || '',
            edition_id: initialData?.edition?.id || '',
            is_visible: initialData?.is_visible || false
        },
        editions: editions || [],
        isEditing: !!initialData?.id,
        courseId: initialData?.id || null,
        isSaving: false,
        errors: {},
        
        async submit() { ... }
    }
}
```

## 7. Integracja API
Komponent komunikuje się z REST API zdefiniowanym w `doc/api-plan.md`.
*   **Tworzenie:** `POST /api/courses/`
*   **Edycja:** `PUT /api/courses/{id}/`
*   **Nagłówki:** `Content-Type: application/json`, `X-CSRFToken` (z ciasteczka).
*   **Obsługa sukcesu:** Przekierowanie do Dashboardu Instruktora lub widoku szczegółów kursu.
*   **Obsługa błędów:** Przypisanie błędów 400 do obiektu `errors`.

## 8. Interakcje użytkownika
1.  **Wejście na stronę:**
    *   **Create:** Formularz jest pusty, domyślna widoczność "Ukryty".
    *   **Edit:** Formularz wypełniony danymi kursu.
2.  **Zmiana widoczności:** Użytkownik klika przełącznik (switch). Stan `is_visible` zmienia się w modelu.
3.  **Wybór edycji:** Użytkownik wybiera edycję (np. semestr) z listy rozwijanej.
4.  **Zapis:**
    *   Kliknięcie "Zapisz".
    *   Przycisk zmienia stan na "ładowanie" (`aria-busy="true"`).
    *   Po sukcesie: Przekierowanie.
    *   Po błędzie: Wyświetlenie komunikatów pod polami.

## 9. Warunki i walidacja
*   **Frontend (HTML5 + Alpine):**
    *   Atrybut `required` dla nazwy, opisu i edycji.
*   **Backend (API):**
    *   Unikalność nazwy (jeśli wymagana przez model).
    *   Poprawność `edition_id` (musi istnieć w tabeli `courses_courseedition`).
    *   Uprawnienia: Tylko Instruktor może tworzyć/edytować kursy.

## 10. Obsługa błędów
*   **Błędy walidacji (400):** Wyświetlane bezpośrednio pod polami formularza (pomocniczy tekst w kolorze czerwonym).
*   **Brak uprawnień (403):** Jeśli użytkownik straci sesję lub uprawnienia, wyświetlany jest komunikat globalny lub przekierowanie do logowania.
*   **Błąd serwera (500):** Wyświetlenie ogólnego komunikatu "Wystąpił błąd podczas zapisywania kursu".

## 11. Kroki implementacji
1.  **Backend (Views):** Utworzenie widoków Django `CourseCreateView` i `CourseUpdateView` renderujących szablon `instructor/course_form.html`. Widoki te muszą pobrać listę edycji (`CourseEdition.objects.all()`) i przekazać ją do kontekstu. Dla edycji, muszą pobrać obiekt kursu i zserializować go do JSON dla Alpine.
2.  **Szablon:** Stworzenie pliku `templates/instructor/course_form.html` z układem Pico.css.
3.  **Alpine Component:** Implementacja logiki `courseForm` w bloku `<script>` w szablonie.
    *   Mapowanie danych wejściowych.
    *   Funkcja `submit` z `fetch`.
    *   Obsługa CSRF.
4.  **Formularz HTML:** Dodanie pól formularza powiązanych `x-model`.
5.  **Stylizacja:** Dopasowanie klas Pico.css (np. `grid` dla przycisków, `role="switch"` dla checkboxa).
6.  **Testy:**
    *   Próba utworzenia kursu bez wymaganych pól.
    *   Poprawne utworzenie kursu.
    *   Edycja istniejącego kursu (zmiana nazwy i widoczności).
    *   Sprawdzenie przekierowania po sukcesie.

