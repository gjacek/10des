# Architektura UI dla Prosta Platforma Dystrybucji Materiałów Kursowych

## 1. Przegląd struktury UI

Architektura interfejsu użytkownika opiera się na modelu hybrydowym, łączącym renderowanie po stronie serwera (Django Templates) z dynamicznymi interakcjami po stronie klienta (Alpine.js).

*   **Layout:** Minimalistyczny, responsywny interfejs oparty na bibliotece **Pico.css**.
*   **Routing:** Zarządzany przez URL dispatcher Django. Każdy widok jest osobną stroną HTML.
*   **Interaktywność:** Formularze, modale, tabele z akcjami oraz obsługa zapytań do API realizowana jest przez **Alpine.js**.
*   **Stan aplikacji:** Token JWT przechowywany w `localStorage`. Stan widoków (np. zawartość listy studentów) pobierany asynchronicznie z API lub wstrzykiwany wstępnie przez Django context.

System posiada dwa odrębne interfejsy w zależności od roli użytkownika (Student vs Prowadzący), ze wspólnym punktem wejścia (Logowanie/Rejestracja).

## 2. Lista widoków

### Strefa Publiczna

#### 1. Strona Główna / Logowanie
*   **Ścieżka:** `/`
*   **Główny cel:** Uwierzytelnienie użytkownika lub przekierowanie do rejestracji.
*   **Kluczowe informacje:** Formularz logowania, link do rejestracji, link do resetu hasła.
*   **Kluczowe komponenty:** `LoginForm` (Alpine.js) obsługujący POST `/api/auth/login/` i zapisujący token.
*   **UX/Bezpieczeństwo:** Przekierowanie zalogowanych użytkowników do odpowiednich dashboardów. Jasne komunikaty błędów logowania.

#### 2. Rejestracja
*   **Ścieżka:** `/register/`
*   **Główny cel:** Utworzenie nowego konta Studenta.
*   **Kluczowe informacje:** Imię, Nazwisko, E-mail, Hasło.
*   **Kluczowe komponenty:** `RegisterForm` z walidacją pól (wymagane, format e-mail).
*   **UX:** Po sukcesie automatyczne przekierowanie do logowania lub autologowanie (zależnie od API flow).

#### 3. Reset hasła
*   **Ścieżka:** `/password-reset/`
*   **Główny cel:** Inicjacja procedury odzyskiwania dostępu.
*   **Kluczowe informacje:** Pole na e-mail.
*   **UX:** Komunikat "Jeśli konto istnieje, wysłano link" (security through obscurity).

---

### Strefa Studenta

#### 4. Moje Kursy (Dashboard Studenta)
*   **Ścieżka:** `/student/my-courses/`
*   **Główny cel:** Szybki dostęp do kursów, do których student ma przyznany dostęp.
*   **Kluczowe informacje:** Lista kart kursów (Nazwa, Edycja, Prowadzący).
*   **Kluczowe komponenty:**
    *   `CourseCard`: Klikalny element przenoszący do szczegółów kursu.
    *   `EmptyState`: Komunikat "Nie jesteś zapisany na żaden kurs" z przyciskiem "Zobacz dostępne kursy".
*   **UX:** Filtrowanie ukrytych kursów (niewidoczne dla studenta nawet jak zapisany).

#### 5. Dostępne Kursy (Katalog)
*   **Ścieżka:** `/student/courses/`
*   **Główny cel:** Przeglądanie oferty i wysyłanie próśb o dołączenie.
*   **Kluczowe informacje:** Lista wszystkich widocznych kursów w systemie. Status relacji studenta z kursem (Brak, Oczekujący, Zapisany, Odrzucony).
*   **Kluczowe komponenty:**
    *   `CourseListItem`: Zawiera przycisk akcji (np. "Wyślij prośbę", "Oczekuje").
    *   `EnrollmentAction`: Komponent Alpine.js obsługujący POST `/api/courses/{id}/enroll/`.
*   **UX:** Blokada przycisku dla statusu "Odrzucony". Dynamiczna zmiana przycisku po wysłaniu prośby.

#### 6. Szczegóły Kursu
*   **Ścieżka:** `/student/courses/<int:id>/`
*   **Główny cel:** Nawigacja po treściach kursu.
*   **Kluczowe informacje:** Metadane kursu, lista **opublikowanych** lekcji posortowana alfabetycznie.
*   **Kluczowe komponenty:**
    *   `LessonList`: Lista linków do widoków lekcji.
*   **Bezpieczeństwo:** Dostęp tylko dla studentów ze statusem `approved`.

#### 7. Widok Lekcji
*   **Ścieżka:** `/student/courses/<int:course_id>/lessons/<int:lesson_id>/`
*   **Główny cel:** Konsumpcja treści i pobieranie plików.
*   **Kluczowe informacje:** Tytuł, opis, lista załączników.
*   **Kluczowe komponenty:**
    *   `AttachmentList`: Lista plików z metadanymi (rozmiar, typ).
    *   `DownloadButton`: Link do endpointu API, który zlicza pobranie i serwuje plik.
*   **UX:** Wyraźne rozróżnienie typów plików (ikony).

---

### Strefa Prowadzącego

#### 8. Dashboard Prowadzącego
*   **Ścieżka:** `/instructor/dashboard/`
*   **Główny cel:** Zarządzanie własnymi kursami.
*   **Kluczowe informacje:** Lista kursów z ich stanem (Widoczny/Ukryty) i licznikiem oczekujących próśb.
*   **Kluczowe komponenty:**
    *   `InstructorCourseTable`: Tabela z kolumnami: Nazwa, Edycja, Status, Oczekujący, Akcje (Edytuj, Lekcje, Zapisy).
    *   `VisibilityToggle`: Przełącznik zmieniający stan kursu (API PATCH).
    *   Przycisk "Utwórz nowy kurs".

#### 9. Kreator / Edycja Kursu
*   **Ścieżka:** `/instructor/courses/create/` oraz `/instructor/courses/<int:id>/edit/`
*   **Główny cel:** Zarządzanie metadanymi kursu.
*   **Kluczowe informacje:** Formularz: Nazwa, Opis, Edycja, Widoczność.
*   **Kluczowe komponenty:** `CourseForm` (Alpine.js).

#### 10. Zarządzanie Lekcjami
*   **Ścieżka:** `/instructor/courses/<int:id>/lessons/`
*   **Główny cel:** Lista lekcji w kursie, dodawanie nowych, zarządzanie statusem publikacji.
*   **Kluczowe informacje:** Tabela lekcji (Tytuł, Status publikacji, Liczba plików).
*   **Kluczowe komponenty:**
    *   `LessonTable`: Z opcjami edycji i usuwania (wymaga potwierdzenia).
    *   `PublishToggle`: Szybka zmiana statusu (Robocza/Opublikowana).
    *   Przycisk "Dodaj lekcję".

#### 11. Edycja Lekcji i Plików
*   **Ścieżka:** `/instructor/courses/<int:course_id>/lessons/<int:lesson_id>/edit/`
*   **Główny cel:** Edycja treści lekcji i zarządzanie załącznikami.
*   **Kluczowe informacje:** Formularz danych lekcji, lista obecnych plików, uploader nowych plików.
*   **Kluczowe komponenty:**
    *   `FileUpload`: Prosty input file (multiple) z listą wybranych plików i przyciskiem "Wyślij". Brak paska postępu, stan "Loading".
    *   `AttachmentManager`: Lista plików z opcją "Usuń".
    *   Walidacja limitów (max 10 plików, max 10MB) - komunikaty tekstowe.

#### 12. Zarządzanie Zapisami
*   **Ścieżka:** `/instructor/courses/<int:id>/enrollments/`
*   **Główny cel:** Decydowanie o dostępie studentów do kursu.
*   **Kluczowe informacje:** Listy studentów podzielone na statusy.
*   **Kluczowe komponenty:**
    *   `EnrollmentTabs`: Przełącznik widoków (Oczekujący | Zapisani | Odrzuceni).
    *   `BulkActionsTable`: Tabela z checkboxami umożliwiająca grupowe akceptowanie/odrzucanie.
    *   `ActionButtons`: Akceptuj, Odrzuć, Przywróć, Usuń (zależnie od zakładki).

## 3. Mapa podróży użytkownika

### Scenariusz: Student zapisuje się na kurs
1.  **Logowanie:** Użytkownik wchodzi na `/`, podaje dane, otrzymuje token JWT -> przekierowanie na `/student/my-courses/`.
2.  **Szukanie:** Lista jest pusta. Użytkownik klika w nawigacji "Dostępne kursy".
3.  **Aplikacja:** Na liście znajduje kurs "Analiza Danych". Klika "Wyślij prośbę". Przycisk zmienia stan na "Oczekiwanie".
4.  **Oczekiwanie:** Student czeka na decyzję Prowadzącego.
5.  **Dostęp:** Po akceptacji, kurs pojawia się w widoku `/student/my-courses/`.
6.  **Konsumpcja:** Student klika w kartę kursu -> widzi listę lekcji -> wchodzi w lekcję -> klika "Pobierz" przy pliku.

### Scenariusz: Prowadzący publikuje materiały
1.  **Dashboard:** Po zalogowaniu widzi `/instructor/dashboard/`.
2.  **Tworzenie:** Klika "Dodaj kurs", wypełnia nazwę i edycję. Kurs jest domyślnie "Ukryty".
3.  **Lekcje:** Wchodzi w "Zarządzaj lekcjami" -> "Dodaj lekcję".
4.  **Treść:** Podaje tytuł, opis, dodaje 3 pliki PDF. Klika "Zapisz".
5.  **Publikacja:** W widoku listy lekcji klika przełącznik przy lekcji na "Opublikowana".
6.  **Udostępnienie kursu:** Wraca do Dashboardu, klika przełącznik "Widoczny" przy kursie.
7.  **Akceptacja:** Widzi licznik "1 oczekujący" przy kursie. Wchodzi w "Zarządzaj zapisami", zaznacza studenta i klika "Akceptuj".

## 4. Układ i struktura nawigacji

Aplikacja wykorzystuje klasyczny układ: **Górny pasek nawigacyjny (Navbar) + Główna zawartość (Container) + Stopka**.

### Navbar
Zawartość paska nawigacyjnego jest dynamiczna i zależy od roli zalogowanego użytkownika (określanej na podstawie danych z JWT/profilu użytkownika w `localStorage`).

*   **Dla Studenta:**
    *   Lewa strona: Logo/Nazwa (link do `/student/my-courses/`).
    *   Środek/Prawa: Linki "Moje Kursy", "Dostępne Kursy".
    *   Prawa skrajna: Dropdown użytkownika (Imię Nazwisko -> Wyloguj).

*   **Dla Prowadzącego:**
    *   Lewa strona: Logo/Nazwa (link do `/instructor/dashboard/`).
    *   Środek/Prawa: Link "Dashboard".
    *   Prawa skrajna: Dropdown użytkownika (Imię Nazwisko -> Wyloguj).

*   **Dla Gościa:**
    *   Lewa strona: Logo/Nazwa.
    *   Prawa strona: Linki "Zaloguj", "Zarejestruj".

### Breadcrumbs (Okruszki)
Dla głębszych struktur (Szczegóły kursu, lekcji) pod paskiem nawigacji wyświetlana jest ścieżka powrotu, np.:
`Dashboard > Analiza Danych 2025 > Lekcja 1`

## 5. Kluczowe komponenty

Poniższe komponenty będą wielokrotnie wykorzystywane w różnych widokach:

1.  **`ApiHandler` (JS Utility):** Centralny wrapper na `fetch`, który automatycznie dodaje nagłówek `Authorization: Bearer ...`, obsługuje odświeżanie tokena (opcjonalnie w v2) oraz przekierowuje na login przy błędzie 401.
2.  **`ToastNotification`:** Dymki powiadomień pojawiające się w rogu ekranu (Sukces: zielony, Błąd: czerwony). Używane do potwierdzania każdej akcji (np. "Zapisano zmiany", "Plik dodany").
3.  **`ConfirmationModal`:** Okno modalne wymagające potwierdzenia akcji destrukcyjnych (np. "Czy na pewno chcesz usunąć tego studenta?"). Zawiera przyciski "Anuluj" i "Potwierdź" (czerwony).
4.  **`LoaderButton`:** Przycisk formularza, który po kliknięciu zmienia stan na "Ładowanie..." i blokuje możliwość ponownego kliknięcia do czasu odpowiedzi z API.
5.  **`StatusBadge`:** Komponent wizualny (pigułka) do oznaczania stanów:
    *   Status zapisu: Oczekujący (żółty), Zapisany (zielony), Odrzucony (czerwony).
    *   Status widoczności: Widoczny (zielony), Ukryty (szary).
6.  **`FileIcon`:** Ikona reprezentująca typ pliku (PDF, ZIP, IMG) wyświetlana obok nazwy załącznika.

