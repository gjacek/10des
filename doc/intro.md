# Projekt Zaliczeniowy: Prosta Platforma do Dystrybucji Materiałów Kursowych

## 1\. Cel Projektu (Executive Summary)

Celem projektu jest stworzenie prostej, minimalistycznej aplikacji webowej (MVP - Minimum Viable Product), która umożliwi **Prowadzącym** udostępnianie materiałów dydaktycznych (pliki + opisy) **Studentom** w ramach zdefiniowanych **Kursów**. Aplikacja skupia się na jednokierunkowej dystrybucji treści i zarządzaniu dostępem do kursów.

## 2\. Użytkownicy i Role

System będzie obsługiwał trzy kluczowe role:

  * **🧑‍🎓 Student:**

      * Może samodzielnie założyć konto (rejestracja).
      * Może przeglądać listę dostępnych kursów.
      * Może wysłać prośbę o dołączenie do wybranego kursu.
      * Po akceptacji przez Prowadzącego, ma dostęp do opublikowanych materiałów w kursie (przeglądanie i pobieranie).

  * **🧑‍🏫 Prowadzący (Instructor):**

      * Konto tworzone i aktywowane przez Administratora.
      * Może tworzyć i zarządzać wieloma **Kursami**.
      * W ramach swoich kursów, może dodawać, edytować i usuwać **Lekcje** (każda lekcja = opis tekstowy + załączniki).
      * Zarządza widocznością lekcji (może je ukrywać lub publikować).
      * Przegląda prośby o dołączenie do jego kursów oraz akceptuje lub odrzuca Studentów.

  * **⚙️ Administrator:**

      * Posiada dostęp do panelu administracyjnego (Django Admin).
      * Głównym zadaniem jest zarządzanie kontami Prowadzących (tworzenie nowych kont, aktywacja, dezaktywacja).

## 3\. Kluczowe Funkcjonalności (Core Features)

### Moduł Uwierzytelniania i Zarządzania Użytkownikami

  * Formularz rejestracji dla Studentów.
  * Formularz logowania dla wszystkich ról.
  * Mechanizm weryfikacji i aktywacji kont Prowadzących (przez Admina).

### Moduł Zarządzania Kursami (Widok Prowadzącego)

  * Tworzenie nowego kursu (nazwa, opis).
  * Dashboard Prowadzącego z listą jego kursów.
  * Zarządzanie zapisami: Widok listy studentów proszących o dostęp do kursu z opcją "Akceptuj" / "Odrzuć".

### Moduł Zarządzania Treścią (Widok Prowadzącego)

  * Wewnątrz kursu, Prowadzący dodaje **Lekcje** (np. "Wykład 1", "Laboratorium 2").
  * Każda Lekcja składa się z:
      * Tytułu (np. "Wprowadzenie do Django").
      * Krótkiego opisu tekstowego (pole `TextField`).
      * Możliwości wgrania jednego lub wielu plików (załączników, np. PDF, ZIP).
  * Każda Lekcja posiada przełącznik "Opublikowana" (boolean), który kontroluje jej widoczność dla Studentów.

### Moduł Konsumpcji Treści (Widok Studenta)

  * Strona główna z listą kursów, do których student ma dostęp.
  * Możliwość wysłania prośby o dołączenie do kursu (jeśli student jeszcze nie jest zapisany).
  * Panel "Dostępne Kursy" z listą wszystkich dostępnych kursów w systemie.
  * Po wejściu w kurs, student widzi listę **tylko opublikowanych** Lekcji.
  * Możliwość wyświetlenia opisu Lekcji i pobrania powiązanych z nią plików.

## 4\. Proponowany Stos Technologiczny

  * **Backend:** **Python 3** z frameworkiem **Django**.
      * Wykorzystanie wbudowanego systemu autentykacji i ról.
      * Wykorzystanie **Django Admin** dla roli Administratora.
      * Django ORM do zarządzania bazą danych.
  * **Frontend:** **HTML5, CSS3, JavaScript (ES6+)**.
      * Renderowanie widoków po stronie serwera (Django Templates).
      * Minimalistyczne użycie **Alpine.js** do obsługi drobnych interakcji UI (np. przełączanie widoczności, proste formularze) bez przeładowywania strony.
  * **Baza danych:** **SQLite** (dla prostoty developmentu) lub **PostgreSQL** (rekomendowane).


## 5\. Funkcjonalności Poza Zakresem (Na Wersję 2.0)

Aby projekt był prosty i wykonalny, **nie będzie** on obejmował:

  * Przesyłania zadań domowych przez studentów.
  * Systemu komentarzy, forum ani czatu.
  * Quizów ani testów.
  * Kalendarza i terminów.
  * Złożonych powiadomień e-mail (poza resetem hasła).
  * Sytemu ocen studentów.