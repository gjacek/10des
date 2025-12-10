# Plan implementacji widoku Reset hasła

## 1. Przegląd
Widok resetu hasła pozwala użytkownikom na zainicjowanie procedury odzyskiwania dostępu do konta poprzez podanie adresu e-mail. System wysyła link resetujący na podany adres (jeśli konto istnieje) i wyświetla stosowny komunikat użytkownikowi.

## 2. Routing widoku
*   **Ścieżka URL:** `/password-reset/`
*   **Nazwa widoku Django:** `password_reset_view`
*   **Plik URLconf:** `kursy/urls.py`

## 3. Struktura komponentów
Widok oparty na szablonach Django (SSR) z logiką po stronie klienta w Alpine.js.

*   `base.html` (Główny layout)
    *   `password_reset.html` (Szablon widoku)
        *   `PasswordResetForm` (Komponent logiczny Alpine.js)
            *   Input: E-mail (`email`)
            *   Button: "Zresetuj hasło" (`submit`)
            *   Alert: Komunikat sukcesu/błędu

## 4. Szczegóły komponentów

### `PasswordResetForm` (Alpine.js Component)
*   **Opis:** Komponent obsługujący formularz wprowadzania adresu e-mail, wysyłkę żądania do API oraz wyświetlanie komunikatów zwrotnych.
*   **Główne elementy HTML:** Tag `<form>` z atrybutem `x-data="passwordResetForm()"`.
*   **Obsługiwane zdarzenia:**
    *   `@submit.prevent="submit"`: Wysłanie formularza.
    *   `@input`: Resetowanie błędów podczas pisania.
*   **Warunki walidacji:**
    *   `email`: Wymagane, format e-mail (HTML5 validation).
*   **Typy (ViewModel):**
    ```typescript
    interface PasswordResetViewModel {
      email: string;
      isLoading: boolean;
      successMessage: string | null;
      errors: {
        email?: string[];
        detail?: string;
      };
    }
    ```
*   **Propsy:** Brak.

## 5. Typy

### DTO (Data Transfer Objects)

**Request (POST /api/auth/password-reset/)**
```json
{
  "email": "string"
}
```

**Response (Success - 200 OK)**
```json
{
  "message": "Wysłano email z informacjami o resecie hasła."
}
```

**Response (Error - 400 Bad Request)**
```json
{
  "message": "Email not found."
}
```
*(Uwaga: Struktura błędu może być również obiektem `{"email": ["..."]}` zależnie od implementacji DRF, należy obsłużyć oba przypadki)*

## 6. Zarządzanie stanem
Stan jest lokalny dla komponentu formularza w Alpine.js.
*   `isLoading`: Blokuje przycisk podczas wysyłania żądania.
*   `successMessage`: Przechowuje treść komunikatu po udanej wysyłce (powoduje ukrycie formularza lub wyświetlenie alertu).
*   `errors`: Przechowuje błędy walidacji.

## 7. Integracja API
*   **Endpoint:** `/api/auth/password-reset/`
*   **Metoda:** `POST`
*   **Nagłówki:** `Content-Type: application/json`
*   **Obsługa odpowiedzi:**
    *   **200 OK:** Ustawienie `successMessage` na treść z odpowiedzi (lub tekst statyczny zgodny z UX).
    *   **400 Bad Request:** Wyświetlenie błędu.
    *   **500 Internal Server Error:** Wyświetlenie ogólnego komunikatu "Wystąpił błąd serwera".

## 8. Interakcje użytkownika
1.  **Wejście na stronę:** Użytkownik widzi prosty formularz z polem e-mail.
2.  **Wypełnienie pola:** Walidacja HTML5 sprawdza format e-maila.
3.  **Wysłanie formularza:**
    *   Przycisk zmienia stan na "Wysyłanie...".
    *   Pola formularza są blokowane (opcjonalnie).
4.  **Sukces (200):**
    *   Formularz zostaje ukryty lub wyczyszczony.
    *   Pojawia się zielony komunikat: "Jeśli konto istnieje, wysłano link z instrukcją resetu hasła."
5.  **Błąd (400/500):**
    *   Przycisk wraca do stanu aktywnego.
    *   Wyświetla się komunikat błędu (nad formularzem lub pod polem).

## 9. Warunki i walidacja
*   **Frontend:** Atrybut `required` oraz `type="email"`.
*   **Backend:** Sprawdzenie istnienia adresu e-mail w bazie danych.

## 10. Obsługa błędów
*   Błędy API są mapowane do obiektu `errors`.
*   Jeśli API zwróci błąd ogólny (`detail` lub `message`), jest on wyświetlany w głównym alercie błędu.
*   Jeśli API zwróci błędy pól (np. `{"email": ["..."]}`), są wyświetlane pod odpowiednim polem.

## 11. Kroki implementacji

1.  **Backend - URL i Widok:**
    *   Dodać wpis `path('password-reset/', views.password_reset_view, name='password_reset')` w `kursy/urls.py`.
    *   Utworzyć prostą funkcję `password_reset_view` w `kursy/views.py` renderującą szablon.

2.  **Frontend - Szablon:**
    *   Utworzyć plik `kursy/templates/registration/password_reset.html`.
    *   Rozszerzyć `base.html`.
    *   Zbudować formularz przy użyciu klas Pico.css.

3.  **Frontend - Logika Alpine.js:**
    *   Zaimplementować obiekt danych `passwordResetForm()`.
    *   Dodać logikę `fetch` do obsługi endpointu `/api/auth/password-reset/`.
    *   Zaimplementować obsługę sukcesu (wyświetlenie komunikatu) i błędów.

4.  **Weryfikacja:**
    *   Test wysyłki dla istniejącego e-maila (powinien pokazać sukces).
    *   Test wysyłki dla nieistniejącego e-maila (zależnie od API: sukces "fake" lub błąd 400).

