<conversation_summary>
<decisions>
1.  Licznik oczekujących studentów nie musi być widoczny na głównym dashboardzie Prowadzącego; wystarczy, że będzie dostępny w dedykowanym widoku zarządzania zapisami do kursu.
2.  Dla MVP walidacja plików (typ, rozmiar, liczba) będzie realizowana wyłącznie po stronie serwera. Interfejs wyświetli jedynie statyczny tekst informacyjny z obowiązującymi limitami.
3.  Użytkownicy niezalogowani nie mają dostępu do publicznej listy kursów. Strona główna dla gościa będzie zawierać wyłącznie formularz logowania i link do rejestracji.
4.  W przypadku wygaśnięcia sesji i przekierowania na stronę logowania, parametr `next` nie jest wymagany w MVP – niezapisane dane w formularzach zostaną utracone.
5.  Nie zakłada się scenariusza jednoczesnej edycji tego samego zasobu przez wielu użytkowników w MVP.
6.  Interfejs nie będzie implementował wskaźników postępu (progress bars) dla przesyłanych plików; wystarczy ogólny wskaźnik ładowania na przycisku akcji.
7.  Sortowanie lekcji w kursie jest alfabetyczne i obowiązuje globalnie, zarówno dla widoku Studenta, jak i Prowadzącego. Ręczna zmiana kolejności nie jest częścią MVP.
8.  Prowadzący w panelu zarządzania zapisami musi mieć możliwość wykonywania akcji na wielu studentach jednocześnie (np. akceptacja kilku próśb za jednym razem).
</decisions>
<matched_recommendations>
1.  **Zarządzanie tokenem:** Token JWT będzie przechowywany w `localStorage` i dołączany do nagłówków `Authorization` w zapytaniach `fetch` realizowanych przez Alpine.js.
2.  **Potwierdzenie serwera:** Każda operacja zapisu danych (CRUD) musi czekać na pomyślną odpowiedź z serwera. Interfejs będzie blokować przycisk akcji i wyświetlać wskaźnik ładowania podczas operacji (brak "optimistic UI").
3.  **Dynamiczne UI:** Stan interfejsu (np. listy studentów) będzie dynamicznie aktualizowany po stronie klienta (przez Alpine.js) w odpowiedzi na pomyślne wykonanie akcji w API, bez przeładowywania całej strony.
4.  **Przekierowanie po logowaniu:** Logika po stronie klienta (JavaScript) po otrzymaniu tokena z API sprawdzi rolę użytkownika i wykona przekierowanie (`window.location.href`) na odpowiedni URL (`/moje-kursy` dla Studenta, `/dashboard-prowadzacego` dla Prowadzącego).
5.  **Status zapisu w API:** Endpoint `GET /api/courses/` zostanie zmodyfikowany tak, aby dla zalogowanego użytkownika zwracał pole `enrollment_status` dla każdego kursu, co pozwoli UI na wyświetlenie odpowiedniego przycisku akcji ("Wyślij prośbę", "Oczekujący" etc.).
6.  **Obsługa błędów:** Błędy walidacji z API (400) będą wyświetlane pod konkretnymi polami formularza. Błędy ogólne (500) i komunikaty sukcesu będą prezentowane jako powiadomienia typu "toast".
7.  **Potwierdzenie akcji destrukcyjnych:** Operacje takie jak usunięcie studenta z kursu czy skasowanie lekcji będą wymagały od użytkownika dodatkowego potwierdzenia w oknie modalnym.
8.  **Stany puste:** Interfejs będzie wyświetlał przyjazne komunikaty i wezwania do działania (CTA), gdy listy danych (np. "Moje kursy") będą puste.
9.  **Interfejs z zakładkami:** Panel zarządzania zapisami będzie oparty na zakładkach ("Oczekujący", "Zapisani", "Odrzuceni") w celu klarownego rozdzielenia grup studentów.
10. **Dostępność modali:** Okna modalne będą programowo zarządzać focusem klawiatury, przenosząc go do wnętrza modala po jego otwarciu i przywracając po zamknięciu.
</matched_recommendations>
<ui_architecture_planning_summary>
Na podstawie przeprowadzonych rozmów, architektura interfejsu użytkownika (UI) dla MVP będzie oparta na renderowanych po stronie serwera szablonach Django, wzbogaconych o dynamiczną interaktywność za pomocą Alpine.js. Fundamentem jest ścisła integracja z zaplanowanym REST API.

**a. Główne wymagania dotyczące architektury UI:**
- **Stack:** Backend Django, szablony HTML, CSS (pico.css), Alpine.js.
- **Wzorce:** Interfejs będzie składał się ze statycznych widoków generowanych przez Django, gdzie poszczególne komponenty (formularze, listy, panele) będą zarządzane przez Alpine.js.
- **Logika:** Wszelkie zmiany stanu danych będą inicjowane przez akcje użytkownika, obsługiwane przez `fetch` w JS, i finalizowane po otrzymaniu potwierdzenia z API.
- **Stan:** Stan aplikacji jest rozproszony i zarządzany lokalnie w poszczególnych komponentach Alpine.js. Globalny stan ogranicza się do tokena JWT przechowywanego w `localStorage`.

**b. Kluczowe widoki, ekrany i przepływy użytkownika:**
- **Gość:** Widzi tylko stronę główną z formularzem logowania, linkiem do rejestracji i resetu hasła. Brak dostępu do jakichkolwiek treści.
- **Student:**
  - Po zalogowaniu jest przekierowywany do widoku "Moje kursy".
  - **Nawigacja:** Główne linki "Moje kursy", "Dostępne kursy"; menu użytkownika z linkami "Mój profil" i "Wyloguj".
  - **Widok "Dostępne kursy":** Lista wszystkich widocznych kursów w systemie. Każdy kurs ma przycisk, którego stan zależy od statusu zapisu studenta (np. "Wyślij prośbę").
  - **Widok "Moje kursy":** Lista kursów, na które student jest zapisany, z przyciskiem "Przejdź do kursu". Kursy ukryte przez Prowadzącego znikają z tej listy.
  - **Widok szczegółów kursu:** Lista opublikowanych lekcji (sortowanych alfabetycznie).
  - **Widok szczegółów lekcji:** Tytuł, opis i lista plików do pobrania w formie bezpośrednich linków `<a>`.
- **Prowadzący:**
  - Po zalogowaniu jest przekierowywany na "Dashboard Prowadzącego".
  - **Nawigacja:** Główny link "Dashboard"; menu użytkownika z linkami "Mój profil" i "Wyloguj".
  - **Dashboard:** Tabela z listą kursów Prowadzącego, ich statusem widoczności i przyciskami akcji ("Zarządzaj zapisami", "Zarządzaj lekcjami", "Edytuj").
  - **Panel zarządzania zapisami:** Interfejs z trzema zakładkami (Oczekujący, Zapisani, Odrzuceni). Każda zakładka zawiera tabelę studentów z checkboxami umożliwiającymi zaznaczenie wielu pozycji i wykonanie akcji grupowej (np. "Akceptuj zaznaczone").
  - **Panel zarządzania lekcjami:** Lista lekcji z etykietą "[WERSJA ROBOCZA]" dla nieopublikowanych i opcjami CRUD.

**c. Strategia integracji z API i zarządzania stanem:**
- Formularze edycji są inicjalizowane danymi wstrzykniętymi przez szablon Django do atrybutu `x-data` w Alpine.js.
- Przesyłanie danych odbywa się asynchronicznie przez `fetch API` z dołączonym tokenem `Bearer`.
- Interfejs użytkownika jest "reaktywny" tylko w odpowiedzi na potwierdzenie z serwera. Po udanej operacji komponent Alpine.js odświeża swoje dane (np. pobierając listę na nowo).
- Pobieranie plików odbywa się przez bezpośrednie linki do endpointów API, które zwracają plik jako załącznik.

**d. Kwestie dotyczące responsywności, dostępności i bezpieczeństwa:**
- **Responsywność:** Zapewniona przez bibliotekę pico.css.
- **Dostępność:** Podstawowe mechanizmy, takie jak zarządzanie focusem w oknach modalnych.
- **Bezpieczeństwo:** Wszelkie akcje destrukcyjne (usunięcie studenta, lekcji) wymagają dodatkowego potwierdzenia w UI. Błąd autoryzacji (`401`) skutkuje natychmiastowym przekierowaniem na stronę logowania.

</ui_architecture_planning_summary>

</conversation_summary>