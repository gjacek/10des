# Schemat Bazy Danych

Na podstawie dokumentu wymagań produktu (PRD) oraz notatek z sesji planowania, poniżej przedstawiono schemat bazy danych dla aplikacji do dystrybucji materiałów kursowych.

## 1. Lista Tabel i ich Struktura

### `users_customuser`
Tabela przechowująca dane użytkowników. Rozszerza standardowy model `User` Django w celu dodania roli Prowadzącego oraz uczynienia imienia i nazwiska polami wymaganymi.

| Kolumna       | Typ danych      | Ograniczenia                     | Opis                                      |
|---------------|-----------------|----------------------------------|-------------------------------------------|
| `id`          | `BIGINT`        | `PRIMARY KEY`                    | Unikalny identyfikator użytkownika.       |
| `password`    | `VARCHAR(128)`  | `NOT NULL`                       | Zahaszowane hasło użytkownika.            |
| `last_login`  | `DATETIME`      | `NULL`                           | Data i czas ostatniego logowania.         |
| `is_superuser`| `BOOLEAN`       | `NOT NULL`                       | Flaga oznaczająca superużytkownika (admina).|
| `email`       | `VARCHAR(254)`  | `NOT NULL`, `UNIQUE`             | Adres e-mail (służy jako login).          |
| `first_name`  | `VARCHAR(150)`  | `NOT NULL`                       | Imię użytkownika.                         |
| `last_name`   | `VARCHAR(150)`  | `NOT NULL`                       | Nazwisko użytkownika.                     |
| `is_staff`    | `BOOLEAN`       | `NOT NULL`                       | Dostęp do panelu administracyjnego Django.|
| `is_active`   | `BOOLEAN`       | `NOT NULL`, `DEFAULT True`       | Oznacza, czy konto jest aktywne.          |
| `date_joined` | `DATETIME`      | `NOT NULL`                       | Data i czas utworzenia konta.             |
| `is_instructor`| `BOOLEAN`      | `NOT NULL`, `DEFAULT False`      | Flaga oznaczająca rolę Prowadzącego.      |

### `courses_courseedition`
Tabela grupująca kursy w edycje, np. semestry akademickie.

| Kolumna | Typ danych     | Ograniczenia             | Opis                                    |
|---------|----------------|--------------------------|-----------------------------------------|
| `id`    | `BIGINT`       | `PRIMARY KEY`            | Unikalny identyfikator edycji.          |
| `name`  | `VARCHAR(255)` | `NOT NULL`, `UNIQUE`     | Nazwa edycji (np. "2025/26 Semestr 2"). |

### `courses_course`
Centralna tabela przechowująca informacje o kursach.

| Kolumna       | Typ danych     | Ograniczenia                                  | Opis                                    |
|---------------|----------------|-----------------------------------------------|-----------------------------------------|
| `id`          | `BIGINT`       | `PRIMARY KEY`                                 | Unikalny identyfikator kursu.           |
| `name`        | `VARCHAR(255)` | `NOT NULL`                                    | Nazwa kursu.                            |
| `description` | `TEXT`         | `NOT NULL`                                    | Opis kursu.                             |
| `is_visible`  | `BOOLEAN`      | `NOT NULL`, `DEFAULT False`                   | Czy kurs jest widoczny publicznie.      |
| `instructor_id`| `BIGINT`      | `FOREIGN KEY (users_customuser.id)`, `NOT NULL`| Klucz obcy do Prowadzącego.             |
| `edition_id`  | `BIGINT`       | `FOREIGN KEY (courses_courseedition.id)`, `NOT NULL`| Klucz obcy do edycji kursu.          |

### `courses_lesson`
Tabela zawierająca lekcje w ramach poszczególnych kursów.

| Kolumna       | Typ danych     | Ograniczenia                              | Opis                                    |
|---------------|----------------|-------------------------------------------|-----------------------------------------|
| `id`          | `BIGINT`       | `PRIMARY KEY`                             | Unikalny identyfikator lekcji.          |
| `title`       | `VARCHAR(255)` | `NOT NULL`                                | Tytuł lekcji.                           |
| `description` | `TEXT`         | `NOT NULL`                                | Opis lekcji.                            |
| `is_published`| `BOOLEAN`      | `NOT NULL`, `DEFAULT False`               | Czy lekcja jest opublikowana.           |
| `course_id`   | `BIGINT`       | `FOREIGN KEY (courses_course.id)`, `NOT NULL`| Klucz obcy do kursu.                 |

### `courses_attachment`
Tabela do przechowywania informacji o plikach-załącznikach do lekcji.

| Kolumna           | Typ danych         | Ograniczenia                               | Opis                                     |
|-------------------|--------------------|--------------------------------------------|------------------------------------------|
| `id`              | `BIGINT`           | `PRIMARY KEY`                              | Unikalny identyfikator załącznika.       |
| `file`            | `VARCHAR(100)`     | `NOT NULL`                                 | Ścieżka do pliku na serwerze.            |
| `original_filename`| `VARCHAR(255)`    | `NOT NULL`                                 | Oryginalna nazwa pliku.                  |
| `download_count`  | `INTEGER UNSIGNED` | `NOT NULL`, `DEFAULT 0`                    | Licznik pobrań pliku.                    |
| `lesson_id`       | `BIGINT`           | `FOREIGN KEY (courses_lesson.id)`, `NOT NULL`| Klucz obcy do lekcji.                 |

### `courses_enrollment`
Tabela pośrednicząca dla relacji Wiele-do-Wielu między studentami a kursami, przechowująca status zapisu.

| Kolumna     | Typ danych    | Ograniczenia                                  | Opis                                                     |
|-------------|---------------|-----------------------------------------------|----------------------------------------------------------|
| `id`        | `BIGINT`      | `PRIMARY KEY`                                 | Unikalny identyfikator rekordu zapisu.                   |
| `status`    | `VARCHAR(10)` | `NOT NULL`, `DEFAULT 'pending'`               | Status zapisu: `pending`, `approved`, `rejected`.        |
| `student_id`| `BIGINT`      | `FOREIGN KEY (users_customuser.id)`, `NOT NULL`| Klucz obcy do studenta.                                  |
| `course_id` | `BIGINT`      | `FOREIGN KEY (courses_course.id)`, `NOT NULL`| Klucz obcy do kursu.                                     |
| -           | -             | `UNIQUE (student_id, course_id)`              | Unikalna para student-kurs, zapobiega duplikatom próśb.  |

## 2. Relacje między Tabelami

- **`users_customuser` ↔ `courses_course` (Jeden-do-Wielu)**
  - Jeden Prowadzący (`users_customuser` gdzie `is_instructor=True`) może być autorem wielu kursów.
  - Relacja zrealizowana przez klucz obcy `courses_course.instructor_id`.
  - Ograniczenie `ON DELETE PROTECT` zapobiega usunięciu Prowadzącego, jeśli ma przypisane kursy.

- **`courses_courseedition` ↔ `courses_course` (Jeden-do-Wielu)**
  - Jedna edycja kursu (`courses_courseedition`) może zawierać wiele kursów.
  - Relacja zrealizowana przez klucz obcy `courses_course.edition_id`.
  - Ograniczenie `ON DELETE PROTECT` zapobiega usunięciu edycji, jeśli są do niej przypisane kursy.

- **`courses_course` ↔ `courses_lesson` (Jeden-do-Wielu)**
  - Jeden kurs może zawierać wiele lekcji.
  - Relacja zrealizowana przez klucz obcy `courses_lesson.course_id`.
  - Ograniczenie `ON DELETE CASCADE` powoduje usunięcie wszystkich lekcji po usunięciu kursu.

- **`courses_lesson` ↔ `courses_attachment` (Jeden-do-Wielu)**
  - Jedna lekcja może zawierać wiele załączników.
  - Relacja zrealizowana przez klucz obcy `courses_attachment.lesson_id`.
  - Ograniczenie `ON DELETE CASCADE` powoduje usunięcie wszystkich załączników po usunięciu lekcji.

- **`users_customuser` ↔ `courses_course` (Wiele-do-Wielu)**
  - Jeden student może być zapisany na wiele kursów, a jeden kurs może mieć wielu studentów.
  - Relacja zrealizowana przez tabelę pośredniczącą `courses_enrollment`.
  - Ograniczenie `ON DELETE CASCADE` usuwa wpis w `courses_enrollment` po usunięciu studenta lub kursu.

## 3. Indeksy

W celu optymalizacji wydajności zapytań, następujące kolumny powinny zostać zindeksowane:

- **Klucze obce**: Wszystkie klucze obce (`instructor_id`, `edition_id`, `course_id`, `lesson_id`, `student_id`) są domyślnie indeksowane przez Django.
- **Pola `UNIQUE`**: Pola z ograniczeniem `UNIQUE` (`users_customuser.email`, `courses_courseedition.name` oraz para `(student_id, course_id)` w `courses_enrollment`) są automatycznie indeksowane.
- **Pola do filtrowania**:
  - `courses_course.is_visible`: Kluczowe dla filtrowania publicznie dostępnych kursów.
  - `courses_lesson.is_published`: Ważne dla wyświetlania opublikowanych lekcji studentom.
  - `courses_enrollment.status`: Usprawnia filtrowanie studentów według statusu zapisu.
  - `users_customuser.is_instructor`: Może przyspieszyć zapytania filtrujące Prowadzących.

## 4. Dodatkowe uwagi

- **Integralność danych**: Zastosowanie `ON DELETE PROTECT` dla relacji z Prowadzącym i Edycją Kursu jest kluczową decyzją biznesową, która chroni przed przypadkową utratą powiązanych danych.
- **Automatyczne ukrywanie kursów**: Logika ukrywania kursów po dezaktywacji Prowadzącego będzie zaimplementowana w warstwie aplikacji (np. przy użyciu sygnałów Django), a nie na poziomie bazy danych.
- **Sortowanie lekcji**: Domyślne sortowanie lekcji alfabetycznie po tytule zostanie zdefiniowane w klasie `Meta` modelu `Lesson` w Django (`ordering = ['title']`), co nie jest bezpośrednio częścią schematu SQL, ale wpływa na działanie aplikacji.
