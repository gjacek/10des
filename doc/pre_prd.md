\<conversation\_summary\>
\<decisions\>

1.  **Model Uwierzytelniania:** Prowadzący rejestrują się przez ten sam formularz co Studenci (Imię, Nazwisko, E-mail, Hasło są obowiązkowe). Administrator nadaje uprawnienia Prowadzącego ręcznie w panelu Admina, po kontakcie poza systemem (np. e-mail od Prowadzącego).
2.  **Zarządzanie Kursami:** Prowadzący nie mogą usuwać kursów. Zamiast tego mają funkcję "Ukryj kurs", która usuwa go z widoku publicznego oraz z listy "Moje Kursy" u już zapisanych Studentów. Kursy domyślnie tworzone są jako "ukryte".
3.  **Metadane Kursu:** Kursy posiadają dodatkowe, jedno pole tekstowe "Edycja Kursu" (np. "2025/26 Semestr 2").
4.  **Zarządzanie Zapisami (Flow):** Proces opiera się wyłącznie na prośbie Studenta i akceptacji Prowadzącego.
5.  **Zarządzanie Zapisami (UI):** Prowadzący zarządza studentami w trzech widokach: "Oczekujący" (opcje: Akceptuj / Odrzuć), "Zapisani" (opcja: Usuń z kursu) oraz "Odrzuceni" (opcja: Przywróć).
6.  **Mechanika Odrzucenia/Przywrócenia:** Odrzucenie studenta blokuje mu możliwość ponownej prośby. "Przywrócenie" studenta z listy odrzuconych automatycznie akceptuje go i zapisuje na kurs.
7.  **Samo-wypisanie:** Student *nie ma* możliwości samodzielnego wypisania się z kursu w MVP.
8.  **Zarządzanie Treścią (Kolejność):** Lekcje w widoku Studenta będą sortowane alfabetycznie po tytule. Bardziej zaawansowane sortowanie (np. ręczne) zostanie rozważone w wersji 2.0.
9.  **Zarządzanie Treścią (Pliki):** Prowadzący może dodawać/usuwać pojedyncze pliki w ramach lekcji. Obowiązują limity: **maksymalnie 10 plików** na lekcję, **maksymalnie 10MB** na pojedynczy plik.
10. **Dezaktywacja Prowadzącego:** Dezaktywacja konta Prowadzącego przez Administratora automatycznie "ukrywa" wszystkie kursy należące do tego Prowadzącego.
11. **Widok Publiczny Kursu:** Niezapisany Student widzi: Nazwę kursu, Opis, Edycję Kursu oraz Nazwisko Prowadzącego wraz z jego adresem e-mail (pobieranym automatycznie z konta).
12. **Kryteria Sukcesu (KPIs):** Dla MVP mierzone będą: 1. Liczba aktywnych Studentów (logowanie min. 1 raz w tygodniu) oraz 2. Łączna liczba pobrań załączników.
13. **Śledzenie Pobrania:** Pobrania będą zliczane poprzez dedykowany widok (view) Django, który pośredniczy w dostarczaniu pliku.

\</decisions\>

\<matched\_recommendations\>

1.  **Identyfikacja Prowadzącego:** Przyjęto model, w którym Prowadzący rejestruje się jak Student, a następnie kontaktuje się z Administratorem poza systemem w celu nadania uprawnień.
2.  **Obowiązkowe pola rejestracji:** Zaakceptowano rekomendację, aby pola "Imię" i "Nazwisko" były obowiązkowe podczas rejestracji w celu łatwiejszej identyfikacji studentów przez Prowadzących.
3.  **Limity plików:** Zaakceptowano rekomendację ustalenia ścisłych limitów technicznych (10 plików na lekcję, 10MB na plik) w celu kontroli kosztów i wydajności.
4.  **Zarządzanie Studentami (CRUD):** Zaakceptowano rekomendację dodania funkcji "Usuń Studenta z kursu" oraz opracowano (na podstawie dyskusji) przepływ "Przywróć Studenta".
5.  **Śledzenie Metryk:** Zaakceptowano rekomendację techniczną, aby śledzić pobrania plików (KPI nr 2) za pomocą pośredniczącego widoku Django, który inkrementuje licznik przed wysłaniem pliku.
6.  **Kontakt do Prowadzącego:** Zaakceptowano rekomendację, aby zapewnić Studentom minimalny kanał kontaktu, wyświetlając e-mail Prowadzącego (pobrany automatycznie z jego konta) w widoku kursu.
7.  **Dezaktywacja Kont:** Zaakceptowano rekomendację, aby dezaktywacja konta Prowadzącego przez Administratora automatycznie ukrywała wszystkie powiązane z nim kursy.
    \</matched\_recommendations\>

\<prd\_planning\_summary\>

### a. Główne Wymagania Funkcjonalne

**Moduł Uwierzytelniania i Role**

  * **Rejestracja (Student/Prowadzący):** Jeden formularz rejestracji wymagający Imienia, Nazwiska, E-maila i Hasła.
  * **Logowanie:** Wspólny formularz logowania.
  * **Panel Admina (Rola: Admin):** Zarządzanie użytkownikami, w tym ręczne nadawanie roli "Prowadzący" użytkownikom po weryfikacji offline. Dezaktywacja kont Prowadzących (co skutkuje ukryciem ich kursów).
  * **Przekierowania:** Student po logowaniu trafia do "Moje Kursy". Prowadzący po logowaniu trafia do "Dashboard Prowadzącego".

**Moduł Zarządzania Kursami (Rola: Prowadzący)**

  * Tworzenie kursu (Nazwa, Opis, pole "Edycja Kursu").
  * Edycja metadanych kursu.
  * Zarządzanie widocznością kursu (przełącznik "Ukryty" / "Widoczny"). Ukrycie blokuje dostęp wszystkim studentom i usuwa kurs z listy publicznej.
  * Brak możliwości trwałego usunięcia kursu przez Prowadzącego.

**Moduł Zarządzania Treścią (Rola: Prowadzący)**

  * W ramach kursu: dodawanie/edycja/usuwanie Lekcji (Tytuł, Opis).
  * Do każdej Lekcji możliwość dodania do 10 plików (max 10MB każdy, wymagana biała lista typów).
  * Zarządzanie pojedynczymi plikami (usuwanie/dodawanie nowych) w edycji lekcji.
  * Zarządzanie widocznością pojedynczej Lekcji (przełącznik "Opublikowana"). Nieopublikowane lekcje mają etykietę [WERSJA ROBOCZA] w panelu Prowadzącego.

**Moduł Zarządzania Zapisami (Rola: Prowadzący)**

  * Panel zarządzania studentami podzielony na 3 listy:
    1.  **Oczekujący:** (Widoczne Imię, Nazwisko, Email). Opcje: "Akceptuj", "Odrzuć".
    2.  **Zapisani:** (Widoczne Imię, Nazwisko, Email). Opcja: "Usuń z kursu".
    3.  **Odrzuceni:** (Widoczne Imię, Nazwisko, Email). Opcja: "Przywróć" (co automatycznie zapisuje studenta).

**Moduł Konsumpcji Treści (Rola: Student)**

  * Widok "Dostępne Kursy" (lista wszystkich widocznych kursów w systemie z opcją "Wyślij prośbę").
  * Widok "Moje Kursy" (lista kursów, na które student jest zapisany).
  * Widok kursu: Lista *tylko opublikowanych* Lekcji, posortowana alfabetycznie po tytule.
  * Widok lekcji: Wyświetlanie opisu i linków do pobrania załączników.

-----

### b. Kluczowe Historie Użytkownika i Ścieżki

  * **Ścieżka Prowadzącego (Tworzenie kursu):**

    1.  Prowadzący rejestruje się jak Student.
    2.  Kontaktuje się z Adminem (poza systemem), prosząc o uprawnienia.
    3.  Admin nadaje mu rolę w panelu Django.
    4.  Prowadzący loguje się, tworzy "Nowy Kurs" (który jest domyślnie ukryty).
    5.  Dodaje do kursu Lekcje i wgrywa pliki (do 10 plików, max 10MB).
    6.  Ustawia przełącznik "Opublikowana" na poszczególnych Lekcjach.
    7.  Gdy kurs jest gotowy, wchodzi w "Edytuj Kurs" i zaznacza "Kurs jest widoczny".

  * **Ścieżka Studenta (Zapis na kurs):**

    1.  Student rejestruje konto (Imię, Nazwisko, Email, Hasło).
    2.  Przegląda listę "Dostępne Kursy".
    3.  Znajduje kurs (widzi jego nazwę, opis, edycję i e-mail Prowadzącego).
    4.  Klika "Wyślij prośbę o dołączenie".
    5.  Czeka na akceptację.

  * **Ścieżka Prowadzącego (Akceptacja):**

    1.  Prowadzący loguje się i wchodzi w zarządzanie swoim kursem.
    2.  Wchodzi do panelu Studentów, na listę "Oczekujący".
    3.  Widzi prośbę (np. "Jan Kowalski, j.kowalski@email.com").
    4.  Klika "Akceptuj".
    5.  Student "Jan Kowalski" pojawia się na liście "Zapisani". Od teraz Student widzi ten kurs na swojej liście "Moje Kursy".

  * **Ścieżka Prowadzącego (Odrzucenie i Przywrócenie):**

    1.  Prowadzący widzi prośbę od nieznanego studenta i klika "Odrzuć".
    2.  Student trafia na listę "Odrzuceni" i nie może aplikować ponownie.
    3.  Po tygodniu Prowadzący orientuje się, że to był błąd.
    4.  Wchodzi na listę "Odrzuceni", znajduje studenta i klika "Przywróć".
    5.  Student jest automatycznie akceptowany i zapisywany na kurs (trafia na listę "Zapisani").

-----

### c. Ważne Kryteria Sukcesu (KPIs)

Aby ocenić sukces MVP, będziemy śledzić dwa kluczowe wskaźniki:

1.  **Adopcja i Aktywność Studentów:** Mierzona jako liczba unikalnych Studentów, którzy zalogowali się do systemu co najmniej raz w ciągu ostatniego tygodnia.
2.  **Zaangażowanie w Treść:** Mierzone jako łączna liczba pobrań wszystkich załączników (plików) z Lekcji przez Studentów.
    \</prd\_planning\_summary\>

\<unresolved\_issues\>

1.  **Biała Lista Typów Plików:** Ustaliliśmy, że będzie stosowana biała lista (whitelist) dozwolonych rozszerzeń plików, ale nie zdefiniowaliśmy jej zawartości. Należy określić listę dopuszczalnych typów (np. `.pdf`, `.zip`, `.pptx`, `.docx`, `.txt`).
    \</unresolved\_issues\>
    \</conversation\_summary\>