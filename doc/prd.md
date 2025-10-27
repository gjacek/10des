# Dokument wymagań produktu (PRD) - Prosta Platforma do Dystrybucji Materiałów Kursowych

## 1. Przegląd produktu

Minimalistyczna aplikacja webowa (MVP) do jednokierunkowej dystrybucji materiałów dydaktycznych przez Prowadzących do Studentów w ramach Kursów. System zapewnia prostą rejestrację, mechanizm zapisu do kursu poprzez prośbę i akceptację, zarządzanie treścią kursów (lekcje i załączniki) oraz podstawowe metryki użycia. Administracja odbywa się głównie przez Django Admin.

Zakres MVP obejmuje: rejestrację i logowanie, rolę Administratora i Prowadzącego, tworzenie i ukrywanie/ujawnianie kursów, dodawanie lekcji z plikami (z limitami), zarządzanie zapisami studentów, widok publiczny kursów, panel konsumpcji treści dla Studentów, podstawowe śledzenie pobrań.

Role użytkowników:
1) Student: rejestruje się samodzielnie, przegląda dostępne kursy, składa prośby o dołączenie, po akceptacji konsumuje opublikowane lekcje i pobiera pliki.
2) Prowadzący: konto tworzone/aktywowane przez Administratora; tworzy i zarządza kursami, lekcjami i zapisami studentów; kontroluje widoczność treści.
3) Administrator: zarządza kontami Prowadzących (tworzenie, aktywacja/dezaktywacja) oraz podstawowymi danymi w Django Admin.

Docelowi użytkownicy i potrzeby:
- Prowadzący: szybka i bezpieczna dystrybucja materiałów bez rozbudowanych funkcji społecznościowych.
- Studenci: łatwy dostęp do materiałów po akceptacji na kurs, bez zbędnych rozpraszaczy.
- Administrator: minimum pracy operacyjnej, użycie wbudowanego panelu administracyjnego.

Założenia technologiczne: Backend Django (Python 3), szablony server-rendered, minimalistyczny front (HTML/CSS/JS z ewentualnym Alpine.js), baza SQLite w dev i PostgreSQL produkcyjnie.

Kluczowe decyzje produktowe (MVP):
- Prowadzący rejestrują się jak Studenci; uprawnienia nadaje Administrator w panelu.
- Kursy są domyślnie ukryte; Prowadzący nie usuwa kursów (może je ukrywać/ujawniać).
- Lekcje mają przełącznik Opublikowana; Studenci widzą wyłącznie opublikowane lekcje.
- Zapis na kurs wyłącznie przez prośbę Studenta i decyzję Prowadzącego (akceptacja/odrzucenie/przywrócenie).
- Limity plików: maks. 10 plików w lekcji, każdy do 10 MB; biała lista rozszerzeń.
- Dezaktywacja Prowadzącego automatycznie ukrywa jego kursy.
- Śledzenie pobrań przez pośredni endpoint.

## 2. Problem użytkownika

Perspektywa Prowadzącego:
- Rozproszone i niekontrolowane udostępnianie materiałów (e-maile, komunikatory) utrudnia aktualizacje i kontrolę dostępu.
- Potrzeba prostego panelu do zarządzania kursami, lekcjami i zapisami bez ciężkiego LMS.

Perspektywa Studenta:
- Trudność w znalezieniu i pobraniu właściwych, aktualnych materiałów dla konkretnych kursów.
- Brak spójnego miejsca z listą kursów oraz jasnym statusem dostępu.

Perspektywa Administratora:
- Chęć minimalizacji prac wdrożeniowych i operacyjnych poprzez wykorzystanie wbudowanego panelu.

Definicja problemu:
Stworzenie łatwego w utrzymaniu, bezpiecznego i czytelnego systemu do dystrybucji materiałów, w którym dostęp do treści jest kontrolowany poprzez prośby o dołączenie, a publikacja treści jest świadomie zarządzana przez Prowadzącego.

## 3. Wymagania funkcjonalne

3.1 Uwierzytelnianie i role
- Rejestracja konta użytkownika (Student/Prowadzący) przez jeden formularz: Imię, Nazwisko, E-mail, Hasło (wymagane pola).
- Logowanie wspólnym formularzem dla wszystkich ról; wylogowanie.
- Administrator nadaje/odbiera rolę Prowadzącego w Django Admin; dezaktywuje konta.
- Po zalogowaniu: Student trafia do Moje Kursy; Prowadzący trafia do Dashboard Prowadzącego.
- Reset hasła przez e-mail (standard mechanizm Django auth).

3.2 Zarządzanie kursami (Prowadzący)
- Tworzenie kursu: Nazwa, Opis, Edycja Kursu (np. 2025/26 Semestr 2); stan widoczności (Ukryty/Widoczny), domyślnie Ukryty.
- Edycja metadanych kursu; zmiana widoczności.
- Brak trwałego usuwania kursu przez Prowadzącego (alternatywa: Ukryj kurs).
- Publiczny widok kursu dla niezalogowanych i niezapisanych: Nazwa, Opis, Edycja Kursu, imię i nazwisko Prowadzącego oraz jego e-mail.
- Dezaktywacja Prowadzącego automatycznie ukrywa wszystkie jego kursy.

3.3 Zarządzanie treścią (Prowadzący)
- Wewnątrz kursu tworzenie lekcji: Tytuł, Opis (tekst), Opublikowana (przełącznik).
- Dodawanie i usuwanie plików w lekcji, z zachowaniem limitów: maks. 10 plików, maks. 10 MB na plik.
- Wymuszenie białej listy typów plików. Minimalny zestaw: .pdf, .zip, .pptx, .docx, .txt .jpg .jpeg (może zostać rozszerzony podczas wdrożenia).
- Lekcje nieopublikowane oznaczone w panelu etykietą (np. [WERSJA ROBOCZA]); dla Studentów niewidoczne.
- Sortowanie lekcji dla Studentów alfabetycznie po tytule.

3.4 Zarządzanie zapisami (Prowadzący/Student)
- Student wysyła prośbę o dołączenie do kursu.
- Prowadzący zarządza trzema listami: Oczekujący (Akceptuj/Odrzuć), Zapisani (Usuń z kursu), Odrzuceni (Przywróć).
- Odrzucenie blokuje ponowną prośbę; Przywrócenie automatycznie akceptuje i zapisuje studenta.
- Po akceptacji Student widzi kurs w Moje Kursy.

3.5 Konsumpcja treści (Student)
- Widok Dostępne Kursy (wszystkie Widoczne kursy w systemie) z możliwością wysłania prośby.
- Widok Moje Kursy (kursy, na które Student ma dostęp).
- Widok kursu: lista tylko opublikowanych lekcji (posortowana po tytule), możliwość pobrania załączników.

3.6 Bezpieczeństwo i autoryzacja
- Dostęp do nieopublikowanych lekcji zablokowany dla Studentów i gości.
- Dostęp do kursów ukrytych zablokowany dla niezapisanych i gości.
- Endpoint pobierania plików pośredniczy i weryfikuje uprawnienia przed wysłaniem pliku.
- Walidacja limitów i typów plików po stronie serwera.

3.7 Śledzenie metryk i audyt
- Każde pobranie pliku zliczane w dedykowanym widoku pobierania.
- Podstawowe logi zdarzeń: utworzenie kursu, publikacja/ukrycie, akceptacje/odrzucenia/przywrócenia.

3.8 Użyteczność i nawigacja
- Przekierowania po logowaniu zależne od roli.
- Czytelne stany w panelu zapisów: Oczekujący, Zapisani, Odrzuceni.
- Etykiety i komunikaty walidacji (np. przekroczono limit plików, niedozwolony typ).

## 4. Granice produktu

Poza zakresem MVP (wersja 2.0):
- Przesyłanie zadań domowych, komentarze/forum/czat, quizy/testy, kalendarz i terminy, złożone powiadomienia e-mail (poza resetem hasła), oceny.

Ograniczenia i decyzje:
- Student nie może samodzielnie wypisać się z kursu w MVP.
- Prowadzący nie usuwa kursów (stosuje Ukryj kurs).
- Biała lista typów plików wymagana; minimalny zestaw określony powyżej, może być rozszerzony operacyjnie.
- Limit 10 plików na lekcję, 10 MB per plik – twarde ograniczenia po stronie serwera i UI.

Ryzyka i zależności:
- Weryfikacja Prowadzących odbywa się poza systemem (kanał e-mail), co wymaga dyscypliny operacyjnej.
- Potencjalne obciążenie pamięci masowej ograniczane przez limity rozmiarów i typów plików.

## 5. Historyjki użytkowników

US-001
Tytuł: Rejestracja użytkownika
Opis: Jako użytkownik chcę utworzyć konto podając Imię, Nazwisko, E-mail i Hasło, aby uzyskać dostęp do systemu.
Kryteria akceptacji:
- Gdy wypełnię wymagane pola i podam unikalny e-mail, po wysłaniu formularza konto zostaje utworzone.
- Gdy pominę któreś z wymaganych pól, widzę komunikat o błędzie i konto nie jest tworzone.

US-002
Tytuł: Logowanie
Opis: Jako użytkownik chcę zalogować się podając e-mail i hasło, aby korzystać z funkcji odpowiednich dla mojej roli.
Kryteria akceptacji:
- Gdy podam poprawne dane, zostaję zalogowany i przekierowany: Student do Moje Kursy, Prowadzący do Dashboardu Prowadzącego.
- Gdy podam niepoprawne dane, pozostaję na stronie logowania z komunikatem o błędzie.

US-003
Tytuł: Reset hasła
Opis: Jako użytkownik chcę zresetować hasło przez e-mail, aby odzyskać dostęp do konta.
Kryteria akceptacji:
- Gdy podam istniejący e-mail, otrzymuję link resetu i mogę ustawić nowe hasło.
- Gdy podam nieistniejący e-mail, system nie ujawnia, czy konto istnieje, i wyświetla komunikat ogólny.

US-004
Tytuł: Nadanie roli Prowadzącego (Admin)
Opis: Jako Administrator chcę nadać użytkownikowi rolę Prowadzącego, aby mógł tworzyć i zarządzać kursami.
Kryteria akceptacji:
- Gdy wybiorę użytkownika w panelu Admin i zaznaczę uprawnienia Prowadzącego, po zapisaniu użytkownik zyskuje dostęp do funkcji Prowadzącego.

US-005
Tytuł: Dezaktywacja Prowadzącego (Admin)
Opis: Jako Administrator chcę dezaktywować konto Prowadzącego, aby uniemożliwić dostęp oraz automatycznie ukryć jego kursy.
Kryteria akceptacji:
- Gdy dezaktywuję Prowadzącego, wszystkie jego kursy stają się Ukryte i znikają z listy Dostępne Kursy.

US-006
Tytuł: Utworzenie kursu (Prowadzący)
Opis: Jako Prowadzący chcę utworzyć kurs z nazwą, opisem i edycją kursu, aby przygotować go do publikacji.
Kryteria akceptacji:
- Gdy utworzę kurs, jego stan widoczności jest Ukryty.
- Wprowadzone pola są walidowane; puste wymagane pola blokują zapis.

US-007
Tytuł: Edycja metadanych kursu (Prowadzący)
Opis: Jako Prowadzący chcę edytować nazwę, opis, edycję kursu oraz widoczność, aby aktualizować informacje.
Kryteria akceptacji:
- Gdy zapiszę zmiany, są one widoczne w odpowiednich widokach; zmiana Widoczny/Ukryty natychmiast wpływa na dostępność kursu.

US-008
Tytuł: Publiczny widok kursu
Opis: Jako niezalogowany użytkownik chcę zobaczyć szczegóły widocznego kursu, aby ocenić jego zawartość przed rejestracją.
Kryteria akceptacji:
- Widzę nazwę, opis, edycję kursu, imię i nazwisko Prowadzącego oraz jego e-mail.
- Nie widzę lekcji ani plików bez zapisu.

US-009
Tytuł: Dodanie lekcji (Prowadzący)
Opis: Jako Prowadzący chcę dodać lekcję z tytułem, opisem i stanem opublikowania, aby udostępnić treści studentom.
Kryteria akceptacji:
- Gdy zapiszę lekcję, może być ona oznaczona jako Opublikowana lub nieopublikowana (wersja robocza).

US-010
Tytuł: Zarządzanie plikami w lekcji (Prowadzący)
Opis: Jako Prowadzący chcę dodawać i usuwać pliki w lekcji, z zachowaniem limitów i białej listy typów, aby kontrolować dystrybucję materiałów.
Kryteria akceptacji:
- Próba dodania pliku spoza białej listy lub >10 MB jest blokowana komunikatem błędu.
- Próba przekroczenia 10 plików w lekcji jest blokowana z komunikatem.

US-011
Tytuł: Publikacja/ukrycie lekcji (Prowadzący)
Opis: Jako Prowadzący chcę przełączać stan opublikowania lekcji, aby kontrolować widoczność dla studentów.
Kryteria akceptacji:
- Gdy lekcja jest nieopublikowana, Studenci jej nie widzą; gdy jest opublikowana, pojawia się w widoku kursu studenta.

US-012
Tytuł: Wysłanie prośby o dołączenie (Student)
Opis: Jako Student chcę wysłać prośbę o dołączenie do widocznego kursu, aby uzyskać dostęp do jego treści.
Kryteria akceptacji:
- Gdy nie jestem zapisany ani odrzucony, mogę wysłać prośbę; status kursu zmienia się na Oczekujący.
- Gdy byłem wcześniej odrzucony, przycisk wysyłki prośby jest niedostępny z odpowiednim komunikatem.

US-013
Tytuł: Akceptacja prośby (Prowadzący)
Opis: Jako Prowadzący chcę zaakceptować prośbę studenta, aby przyznać mu dostęp do kursu.
Kryteria akceptacji:
- Po akceptacji student pojawia się na liście Zapisani; student widzi kurs w Moje Kursy.

US-014
Tytuł: Odrzucenie prośby (Prowadzący)
Opis: Jako Prowadzący chcę odrzucić prośbę studenta, aby zablokować mu dostęp do kursu.
Kryteria akceptacji:
- Po odrzuceniu student trafia na listę Odrzuceni i nie może ponownie aplikować.

US-015
Tytuł: Przywrócenie odrzuconego studenta (Prowadzący)
Opis: Jako Prowadzący chcę przywrócić wcześniej odrzuconego studenta, aby automatycznie zapisać go na kurs.
Kryteria akceptacji:
- Po przywróceniu student trafia na listę Zapisani i widzi kurs w Moje Kursy.

US-016
Tytuł: Usunięcie studenta z kursu (Prowadzący)
Opis: Jako Prowadzący chcę usunąć studenta z listy Zapisani, aby cofnąć mu dostęp.
Kryteria akceptacji:
- Po usunięciu student znika z listy Zapisani i traci dostęp do kursu.

US-017
Tytuł: Widok Dostępne Kursy (Student)
Opis: Jako Student chcę przeglądać wszystkie widoczne kursy w systemie, aby wybrać te, do których chcę dołączyć.
Kryteria akceptacji:
- Lista pokazuje wyłącznie kursy w stanie Widoczny; dla każdego kursu dostępny jest przycisk Wyślij prośbę (jeśli dopuszczalne).

US-018
Tytuł: Widok Moje Kursy (Student)
Opis: Jako Student chcę widzieć listę kursów, na które mam dostęp, aby szybko do nich przechodzić.
Kryteria akceptacji:
- Lista zawiera wyłącznie kursy z akceptacją; kursy ukryte Prowadzącego nie są widoczne.

US-019
Tytuł: Widok kursu z opublikowanymi lekcjami (Student)
Opis: Jako Student chcę widzieć w kursie tylko opublikowane lekcje, posortowane alfabetycznie, aby łatwo odnaleźć materiały.
Kryteria akceptacji:
- Widoczne są wyłącznie lekcje opublikowane; kolejność alfabetyczna po tytule.

US-020
Tytuł: Pobieranie pliku z lekcji (Student)
Opis: Jako Student chcę pobierać pliki z opublikowanych lekcji kursów, do których mam dostęp.
Kryteria akceptacji:
- Pobranie jest możliwe tylko dla zapisanych studentów; każde pobranie jest zliczane.

US-021
Tytuł: Bezpieczny dostęp do zasobów (Autoryzacja)
Opis: Jako system chcę weryfikować uprawnienia przed udostępnieniem plików, lekcji i kursów, aby chronić treści przed nieuprawnionym dostępem.
Kryteria akceptacji:
- Gość lub użytkownik niezapisany otrzymuje przekierowanie/komunikat braku uprawnień przy próbie dostępu do kursu/lekcji/pliku.
- Student nie widzi nieopublikowanych lekcji i nie może pobrać ich plików.

US-022
Tytuł: Przekierowania po logowaniu
Opis: Jako użytkownik chcę być przekierowany po logowaniu zgodnie z moją rolą, aby szybciej rozpocząć pracę.
Kryteria akceptacji:
- Student trafia do Moje Kursy, Prowadzący do Dashboardu Prowadzącego.

US-023
Tytuł: Blokada ponownej prośby po odrzuceniu (Student)
Opis: Jako Student, który został odrzucony, nie chcę móc ponownie aplikować, aby uniknąć spamowania Prowadzącego.
Kryteria akceptacji:
- Przyciski wysyłki prośby są nieaktywne, a UI informuje o statusie Odrzucony.

US-024
Tytuł: Ukrycie kursu (Prowadzący)
Opis: Jako Prowadzący chcę ukryć kurs, aby tymczasowo wstrzymać jego dostępność dla Studentów i gości.
Kryteria akceptacji:
- Ukryty kurs znika z Dostępne Kursy i z widoków Studentów (także zapisanych), aż do ponownego ujawnienia.

US-025
Tytuł: Sortowanie lekcji (Student)
Opis: Jako Student chcę, aby lekcje były posortowane alfabetycznie po tytule, aby szybciej znajdować treści.
Kryteria akceptacji:
- Kolejność lekcji w widoku kursu jest alfabetyczna po tytule.

US-026
Tytuł: Walidacja typów plików (Prowadzący)
Opis: Jako Prowadzący chcę, aby niedozwolone typy plików były blokowane, aby spełnić wymagania bezpieczeństwa i wydajności.
Kryteria akceptacji:
- Dodanie pliku o rozszerzeniu spoza białej listy jest blokowane z komunikatem o niedozwolonym typie.

US-027
Tytuł: Automatyczne ukrycie kursów przy dezaktywacji (System)
Opis: Jako system chcę automatycznie ukrywać kursy dezaktywowanego Prowadzącego, aby uniemożliwić dostęp do jego treści.
Kryteria akceptacji:
- Po dezaktywacji konta Prowadzącego wszystkie jego kursy natychmiast mają stan Ukryty.
 
US-028
Tytuł: Dashboard Prowadzącego
Opis: Jako Prowadzący chcę widzieć dashboard z listą moich kursów i skrótami do zarządzania, aby szybko przechodzić do tworzenia/edycji kursu, lekcji i zapisów.
Kryteria akceptacji:
- Widzę listę wszystkich moich kursów z informacją o widoczności (Widoczny/Ukryty) i liczbie oczekujących próśb.
- Dla każdego kursu dostępne są akcje: Edytuj kurs, Zarządzaj lekcjami, Zarządzaj zapisami.

US-029
Tytuł: Panel zarządzania zapisami (UI)
Opis: Jako Prowadzący chcę panel z trzema listami (Oczekujący, Zapisani, Odrzuceni), aby intuicyjnie zarządzać dostępem.
Kryteria akceptacji:
- Lista Oczekujący wyświetla imię, nazwisko i e-mail oraz oferuje akcje Akceptuj/Odrzuć dla każdego wniosku.
- Lista Zapisani oferuje akcję Usuń z kursu.
- Lista Odrzuceni oferuje akcję Przywróć.

US-030
Tytuł: Oznaczenie wersji roboczej lekcji (Prowadzący)
Opis: Jako Prowadzący chcę, aby nieopublikowane lekcje były oznaczone etykietą [WERSJA ROBOCZA] w moim panelu, aby łatwo je odróżnić.
Kryteria akceptacji:
- Lekcje nieopublikowane wyświetlają etykietę [WERSJA ROBOCZA] w listach i widokach edycji Prowadzącego.

US-031
Tytuł: Widok szczegółów lekcji (Student)
Opis: Jako Student chcę otworzyć widok lekcji, aby przeczytać jej opis i pobrać powiązane pliki.
Kryteria akceptacji:
- Widzę tytuł lekcji, opis oraz listę plików do pobrania wyłącznie dla lekcji opublikowanych w kursach, do których mam dostęp.

## 6. Metryki sukcesu

Metryki główne (KPIs):
1) Aktywność Studentów: liczba unikalnych studentów, którzy zalogowali się co najmniej raz w ciągu ostatniego tygodnia.
2) Zaangażowanie w treść: łączna liczba pobrań wszystkich załączników z lekcji przez studentów.

Definicje i pomiar:
- Aktywność Studentów mierzona na podstawie logów logowania (ostatnie 7 dni, deduplikacja po użytkowniku).
- Licznik pobrań inkrementowany w pośrednim endpointzie pobierania przed wysyłką pliku.
