<conversation_summary>
<decisions>
1. Model użytkownika będzie niestandardowym modelem (`CustomUser`) dziedziczącym po `AbstractUser`, z dodanym polem logicznym `is_instructor` do oznaczania Prowadzących. Pola `first_name` i `last_name` będą wymagane.
2. Relacja między Użytkownikiem a Kursem zostanie zrealizowana przez jawny model pośredniczący `Enrollment`, który będzie zawierał pole `status` ze stanami: 'pending', 'approved', 'rejected'.
3. Usunięcie studenta z kursu przez prowadzącego powoduje zmianę statusu w modelu `Enrollment` na 'rejected', a nie fizyczne usunięcie rekordu.
4. Ukrywanie kursów będzie realizowane przez pole logiczne `is_visible` w modelu `Course`.
5. Model `Attachment` będzie posiadał `FileField` z walidacją oraz pole `original_filename` do przechowywania oryginalnej nazwy pliku. Licznik pobrań (`download_count`) będzie inkrementowany atomowo.
6. Logika automatycznego ukrywania kursów po dezaktywacji prowadzącego zostanie zaimplementowana w warstwie aplikacji (sygnały), bez wpływu na schemat bazy.
7. Ochrona przed usunięciem Prowadzącego lub Edycji kursu, do których przypisane są kursy, zostanie zrealizowana na poziomie ORM (`on_delete=models.PROTECT`).
8. Zostanie stworzony model `CourseEdition` do grupowania kursów; model `Course` będzie miał do niego klucz obcy.
9. Nazwa kursu może się powtarzać; nie będzie stosowane ograniczenie unikalności.
10. Zrezygnowano z tworzenia dedykowanych menedżerów QuerySet (`CourseManager`, `LessonManager`) na etapie MVP.
11. Zrezygnowano z tworzenia modelu `AuditEvent` na etapie MVP.
12. Zrezygnowano z dodawania pól `created_at` i `updated_at` do modeli na etapie MVP.
</decisions>
<matched_recommendations>
1. **Model Użytkownika:** Stworzenie niestandardowego modelu `CustomUser` dziedziczącego po `AbstractUser`, z polami `first_name`, `last_name` jako wymaganymi (`blank=False`, dodane do `REQUIRED_FIELDS`) oraz polem logicznym `is_instructor` do identyfikacji Prowadzących.
2. **Model Zapisu (`Enrollment`):** Użycie jawnego modelu pośredniczącego dla relacji Wiele-do-Wielu (`User`-`Course`) z polem `status` typu `CharField` z `choices=['pending', 'approved', 'rejected']` i wartością domyślną `default='pending'`.
3. **Model Kursu (`Course`):** Model będzie zawierał pole `is_visible` (`BooleanField`, `default=False`). Klucz obcy do instruktora (`User`) powinien używać `on_delete=models.PROTECT` i `limit_choices_to={'is_instructor': True}`.
4. **Model Załącznika (`Attachment`):** Stworzenie modelu z `FileField` wykorzystującym `upload_to` do dynamicznego generowania ścieżek, polem `original_filename` (`CharField`) oraz polem `download_count` (`PositiveIntegerField`, `default=0`).
5. **Model Edycji Kursu (`CourseEdition`):** Stworzenie osobnego modelu `CourseEdition` i połączenie go z modelem `Course` za pomocą klucza obcego (`ForeignKey`).
6. **Sortowanie Lekcji:** Zastosowanie `ordering = ['title']` w klasie `Meta` modelu `Lesson`, aby zapewnić domyślne sortowanie alfabetyczne.
7. **Wartości domyślne:** Ustawienie atrybutu `default` w kluczowych polach statusu: `Course.is_visible` (False), `Lesson.is_published` (False) i `Enrollment.status` ('pending').
</matched_recommendations>
<database_planning_summary> 
Na podstawie przeprowadzonej analizy dokumentu wymagań (PRD) i dyskusji, celem jest stworzenie schematu bazy danych dla MVP platformy do dystrybucji materiałów kursowych. Schemat ma wspierać trzy role użytkowników, hierarchiczną strukturę treści oraz kontrolowany dostęp do materiałów.

**a. Główne wymagania dotyczące schematu bazy danych**
- Implementacja systemu ról (Student, Prowadzący, Administrator) w ramach jednego modelu użytkownika.
- Struktura danych: Kursy są przypisane do Edycji i Prowadzących. Kursy składają się z Lekcji, a Lekcje mogą zawierać wiele Załączników.
- Zarządzanie dostępem: System zapisu na kurs oparty na prośbach i decyzjach, z trzema stanami (oczekujący, zapisany, odrzucony). Widoczność kursów i publikacja lekcji kontrolowane przez Prowadzącego za pomocą flag logicznych.
- Obsługa plików: Przechowywanie plików z walidacją (w logice aplikacji), przechowywanie oryginalnej nazwy pliku i zliczanie pobrań.

**b. Kluczowe encje i ich relacje**
- **User** (`CustomUser`): Dziedziczy po `AbstractUser`. Posiada pole `is_instructor` (`BooleanField`).
- **CourseEdition**: Przechowuje nazwę edycji kursu (np. "2025/26 Semestr 2").
- **Course**: Centralna encja. Zawiera `name`, `description`, `is_visible` (`BooleanField`). Posiada relacje `ForeignKey` do `User` (jako instruktor) i `CourseEdition`.
- **Lesson**: Encja podrzędna do `Course`. Zawiera `title`, `description`, `is_published` (`BooleanField`). Posiada `ForeignKey` do `Course`.
- **Attachment**: Encja podrzędna do `Lesson`. Zawiera `file` (`FileField`), `original_filename` (`CharField`) i `download_count` (`PositiveIntegerField`). Posiada `ForeignKey` do `Lesson`.
- **Enrollment**: Model pośredniczący (`through`) dla relacji Wiele-do-Wielu między `User` a `Course`. Przechowuje `status` zapisu (`CharField`) oraz klucze obce do `User` i `Course`.

**c. Ważne kwestie dotyczące bezpieczeństwa i skalowalności**
- **Bezpieczeństwo dostępu**: Logika dostępu będzie zaimplementowana w aplikacji w oparciu o flagi `is_visible`, `is_published` oraz status w modelu `Enrollment`.
- **Integralność danych**: Zastosowanie `on_delete=models.PROTECT` na kluczach obcych `Course.instructor` oraz `Course.edition` zapobiegnie przypadkowemu usunięciu danych, które są w użyciu.
- **Wydajność**: Pola używane do filtrowania (`is_visible`, `is_published`, `status`) powinny zostać zindeksowane (`db_index=True`) w celu optymalizacji zapytań. Atomowa inkrementacja licznika pobrań za pomocą `F()` zapewni wydajność i spójność przy dużej liczbie jednoczesnych pobrań.

</database_planning_summary>
<unresolved_issues>
Na podstawie przeprowadzonej konwersacji wszystkie kluczowe kwestie dotyczące schematu bazy danych dla wersji MVP zostały wyjaśnione i uzgodnione. Nie zidentyfikowano istotnych nierozwiązanych problemów. Następnym krokiem jest implementacja zdefiniowanych modeli w Django.
</unresolved_issues>
</conversation_summary>