# Plan implementacji widoku Zarządzania Zapisami (Enrollment Management)

## 1. Przegląd
Widok "Zarządzanie Zapisami" (Enrollment Management) jest kluczowym elementem panelu instruktora, umożliwiającym kontrolę dostępu studentów do kursu. Pozwala Prowadzącemu na przeglądanie list studentów w podziale na statusy (Oczekujący, Zapisani, Odrzuceni) oraz wykonywanie akcji decyzyjnych (akceptacja, odrzucenie, przywrócenie, usunięcie), zarówno pojedynczo, jak i masowo.

## 2. Routing widoku
*   **Ścieżka URL:** `/instructor/courses/<int:id>/enrollments/`
*   **Nazwa URL:** `instructor_course_enrollments`
*   **Dostęp:** Tylko dla zalogowanych Prowadzących (właścicieli kursu).

## 3. Struktura komponentów
Widok zostanie zbudowany jako hybryda szablonu Django (struktura) i Alpine.js (interaktywność).

Hierarchia logiczna (Alpine.js Components):
*   `EnrollmentManager` (Główny kontener `x-data`)
    *   `TabNavigation` (Pasek zakładek statusów)
    *   `BulkActionBar` (Pasek akcji grupowych - warunkowy)
    *   `EnrollmentTable` (Tabela danych)
        *   `TableHead` (Sortowanie, Select All)
        *   `TableRow` (Wiersz danych, Checkbox, Inline Actions)
    *   `LoadingIndicator` (Spinner ładowania)
    *   `EmptyState` (Komunikat o braku danych)
    *   `NotificationToast` (Powiadomienia o sukcesie/błędzie)

## 4. Szczegóły komponentów

### 1. `EnrollmentManager` (Kontener)
*   **Opis:** Główny wrapper zarządzający stanem widoku, pobieraniem danych i koordynacją akcji.
*   **Element HTML:** `div` z atrybutem `x-data="enrollmentManager(courseId)"`.
*   **Główne elementy:** Zawiera wszystkie poniższe komponenty.
*   **Obsługiwane zdarzenia:** Inicjalizacja (`x-init`), obsługa błędów globalnych.

### 2. `TabNavigation`
*   **Opis:** Przełącznik między listami studentów.
*   **Element HTML:** Grupa przycisków lub lista linków (zgodnie z pico.css `role="group"`).
*   **Stany:**
    *   `Pending` (Oczekujący)
    *   `Approved` (Zapisani)
    *   `Rejected` (Odrzuceni)
*   **Interakcje:** Kliknięcie zmienia `activeTab` i wyzwala pobranie danych.

### 3. `EnrollmentTable`
*   **Opis:** Tabela wyświetlająca listę studentów dla aktualnego statusu.
*   **Kolumny:**
    *   Checkbox (wybór)
    *   Student (Imię i Nazwisko)
    *   Email
    *   Data zgłoszenia/zmiany (jeśli dostępna w API)
    *   Akcje (przyciski pojedyncze)
*   **Logika:** Renderowanie pętli `x-for="enrollment in enrollments"`.

### 4. `BulkActionBar`
*   **Opis:** Pasek pojawiający się, gdy zaznaczono co najmniej jeden rekord (`selectedIds.length > 0`).
*   **Akcje:** Zależne od aktywnej zakładki (np. dla 'Pending': "Akceptuj wybrane", "Odrzuć wybrane").

## 5. Typy (DTO i ViewModel)

Wymagane struktury danych (odzwierciedlające JSON response z API):

### `StudentDTO`
```typescript
{
    id: number;
    first_name: string;
    last_name: string;
    email: string;
}
```

### `EnrollmentDTO`
```typescript
{
    id: number;
    status: 'pending' | 'approved' | 'rejected';
    student: StudentDTO;
    // opcjonalnie data utworzenia, jeśli API zwróci
}
```

### `EnrollmentState` (Alpine Store)
```typescript
{
    courseId: number;
    activeTab: 'pending' | 'approved' | 'rejected';
    enrollments: EnrollmentDTO[];
    selectedIds: number[]; // ID zaznaczonych zapisów
    isLoading: boolean;
    error: string | null;
    successMessage: string | null;
}
```

## 6. Zarządzanie stanem
Stan będzie zarządzany lokalnie w komponencie Alpine.js (`x-data`). Nie jest wymagany globalny store (Pinia/Redux), ponieważ stan jest lokalny dla tego widoku.

Pola stanu:
*   `activeTab`: Domyślnie 'pending'.
*   `enrollments`: Lista pobrana z API.
*   `selection`: Zbiór (Set lub Array) ID zaznaczonych wierszy.

Metody stanu:
*   `fetchEnrollments()`: Pobiera dane dla `activeTab`.
*   `toggleSelect(id)`: Dodaje/usuwa ID z zaznaczenia.
*   `toggleSelectAll()`: Zaznacza/odznacza wszystkie widoczne.
*   `executeAction(actionType, ids)`: Wykonuje żądanie API (bulk lub single).

## 7. Integracja API

Wykorzystanie endpointów zdefiniowanych w `api-plan.md`. Komunikacja via `fetch` z obsługą nagłówków autoryzacyjnych (CSRFToken dla sesji Django).

### Pobieranie listy
*   **Endpoint:** `GET /api/courses/{course_id}/enrollments/`
*   **Parametry:** `?status={activeTab}`
*   **Odpowiedź:** Lista obiektów `EnrollmentDTO`.

### Akcje masowe (i pojedyncze)
Użycie endpointu bulk-update jest preferowane dla spójności obsługi tabeli.
*   **Endpoint:** `POST /api/courses/{course_id}/enrollments/bulk-update/`
*   **Body:**
    ```json
    {
        "enrollment_ids": [1, 2, 3],
        "action": "approve" | "reject" | "delete" | "restore"
    }
    ```
*   **Mapowanie akcji:**
    *   Zakładka Pending -> akcje: `approve`, `reject`.
    *   Zakładka Approved -> akcje: `delete` (usuń z kursu).
    *   Zakładka Rejected -> akcje: `restore` (przywróć do approved).

## 8. Interakcje użytkownika

1.  **Zmiana zakładki:**
    *   Użytkownik klika "Zapisani".
    *   UI czyści `selectedIds`.
    *   UI pokazuje loader.
    *   Pobranie danych `status=approved`.
    *   Renderowanie tabeli.

2.  **Zaznaczanie:**
    *   Kliknięcie checkboxa wiersza -> aktualizacja licznika zaznaczonych.
    *   Kliknięcie "Zaznacz wszystkie" -> toggle wszystkich widocznych rekordów.

3.  **Akcja (np. Akceptuj):**
    *   Użytkownik klika "Akceptuj" (w wierszu lub w pasku masowym).
    *   Wywołanie API `bulk-update` z `action='approve'`.
    *   Po sukcesie: Wyświetlenie toasta "Zaakceptowano X studentów", odświeżenie listy (usunięcie przetworzonych rekordów z widoku).

## 9. Warunki i walidacja

*   **Transakcyjność:** Operacje `bulk-update` muszą być wykonywane w bloku `transaction.atomic`, aby zapewnić spójność danych (wszystkie albo żaden).
*   **Walidacja wyboru:** Przyciski akcji masowych są `disabled`, gdy `selectedIds` jest puste.
*   **Spójność akcji:**
    *   W zakładce `Pending` nie można wywołać akcji `restore` ani `delete`.
    *   W zakładce `Approved` dostępna tylko akcja `delete` (usuń z kursu).
    *   W zakładce `Rejected` dostępna tylko akcja `restore`.
*   **Zabezpieczenie przed pustym żądaniem:** Frontend blokuje wysyłkę pustej listy ID.

## 10. Obsługa błędów

*   **Błąd transakcji:** Jeśli wystąpi błąd podczas operacji masowej (np. jeden rekord zablokowany), cała operacja jest wycofywana, a użytkownik widzi komunikat: "Wystąpił błąd podczas przetwarzania. Żadne zmiany nie zostały zapisane."
*   **Błąd transakcji:** Jeśli wystąpi błąd podczas operacji masowej (np. jeden rekord zablokowany), cała operacja jest wycofywana, a użytkownik widzi komunikat: "Wystąpił błąd podczas przetwarzania. Żadne zmiany nie zostały zapisane."
*   **Błąd sieci/API:** Wyświetlenie alertu (czerwony box) nad tabelą z komunikatem błędu (np. "Nie udało się pobrać listy", "Błąd serwera przy akceptacji").
*   **Brak uprawnień (403):** Przekierowanie do logowania lub komunikat "Brak uprawnień".
*   **Empty State:** Jeśli API zwróci pustą listę, wyświetlenie przyjaznego komunikatu "Brak oczekujących wniosków" zamiast pustej tabeli.

## 11. Kroki implementacji

1.  **Backend - Widok (Template View):**
    *   Stworzenie klasy `EnrollmentManagerView` (TemplateView) w `kursy/views.py` (lub `instructor_views.py`).
    *   Zabezpieczenie widoku `LoginRequiredMixin` + weryfikacja czy user jest instruktorem tego kursu.
    *   Przekazanie `course_id` do kontekstu szablonu.

2.  **Frontend - Szablon Bazowy:**
    *   Stworzenie pliku `kursy/templates/instructor/enrollment_manager.html`.
    *   Rozszerzenie `base.html`.
    *   Dodanie struktury HTML dla zakładek i tabeli.

3.  **Frontend - Alpine Logic:**
    *   Implementacja obiektu `enrollmentManager` w tagu `<script>`.
    *   Implementacja metody `fetchData`.
    *   Implementacja metod `toggle` i logiki checkboxów.

4.  **Frontend - Integracja API:**
    *   Implementacja funkcji pomocniczej `getCsrfToken()`.
    *   Podpięcie metody `performAction` pod przyciski API.

5.  **Stylowanie i UI:**
    *   Dostosowanie tabeli do Pico.css (klasa `striped`).
    *   Dodanie stylów dla stanów (np. badge statusów).

6.  **Testowanie Manualne:**
    *   Weryfikacja przepływu: Student wysyła prośbę -> Instruktor widzi w Pending -> Akceptuje -> Student w Approved.

