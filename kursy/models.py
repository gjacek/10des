from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Rozszerzony model użytkownika Django.

    Dodaje pole is_instructor do oznaczenia prowadzących kursów.
    Wymaga podania imienia i nazwiska przy rejestracji.
    """
    is_instructor = models.BooleanField(
        default=False,
        verbose_name="Prowadzący",
        help_text="Oznacza, czy użytkownik jest prowadzącym kursy."
    )

    class Meta:
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class CourseEdition(models.Model):
    """
    Model reprezentujący edycję kursu (np. semestr akademicki).

    Grupuje kursy w poszczególne edycje/semestry.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Nazwa edycji",
        help_text="Nazwa edycji kursu (np. '2025/26 Semestr 2')."
    )

    class Meta:
        verbose_name = "Edycja kursu"
        verbose_name_plural = "Edycje kursów"
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Centralny model kursu.

    Przechowuje informacje o kursach wraz z prowadzącym i edycją.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Nazwa kursu",
        help_text="Nazwa kursu."
    )
    description = models.TextField(
        verbose_name="Opis kursu",
        help_text="Szczegółowy opis kursu."
    )
    is_visible = models.BooleanField(
        default=False,
        verbose_name="Widoczny publicznie",
        help_text="Czy kurs jest widoczny dla wszystkich użytkowników.",
        db_index=True
    )
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        limit_choices_to={'is_instructor': True},
        related_name='courses',
        verbose_name="Prowadzący",
        help_text="Prowadzący kurs."
    )
    edition = models.ForeignKey(
        CourseEdition,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Edycja kursu",
        help_text="Edycja/semestr, do którego należy kurs."
    )

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kursy"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.edition})"


class Lesson(models.Model):
    """
    Model lekcji w ramach kursu.

    Przechowuje informacje o poszczególnych lekcjach.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Tytuł lekcji",
        help_text="Tytuł lekcji."
    )
    description = models.TextField(
        verbose_name="Opis lekcji",
        help_text="Szczegółowy opis lekcji."
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Opublikowana",
        help_text="Czy lekcja jest opublikowana i dostępna dla studentów.",
        db_index=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Kurs",
        help_text="Kurs, do którego należy lekcja."
    )

    class Meta:
        verbose_name = "Lekcja"
        verbose_name_plural = "Lekcje"
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.course})"

def lesson_attachment_path(instance, filename):
    # Plik zostanie zapisany w MEDIA_ROOT/attachments/course_<id>/lesson_<id>/<filename>
    return f'attachments/course_{instance.lesson.course.id}/lesson_{instance.lesson.id}/{filename}'

class Attachment(models.Model):
    """
    Model załącznika do lekcji.

    Przechowuje informacje o plikach dołączonych do lekcji.
    """
    file = models.FileField(
        upload_to=lesson_attachment_path,
        verbose_name="Plik",
        help_text="Ścieżka do pliku na serwerze."
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name="Oryginalna nazwa pliku",
        help_text="Oryginalna nazwa pliku przesłanego przez użytkownika."
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Liczba pobrań",
        help_text="Liczba pobrań pliku."
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Lekcja",
        help_text="Lekcja, do której należy załącznik."
    )

    class Meta:
        verbose_name = "Załącznik"
        verbose_name_plural = "Załączniki"
        ordering = ['original_filename']

    def __str__(self):
        return f"{self.original_filename} ({self.lesson})"


class Enrollment(models.Model):
    """
    Model zapisu na kurs.

    Reprezentuje relację wiele-do-wielu między studentami a kursami
    z dodatkowymi informacjami o statusie zapisu.
    """

    STATUS_CHOICES = [
        ('pending', 'Oczekujący'),
        ('approved', 'Zatwierdzony'),
        ('rejected', 'Odrzucony'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status zapisu",
        help_text="Status zapisu na kurs.",
        db_index=True
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'is_instructor': False},
        related_name='enrollments',
        verbose_name="Student",
        help_text="Student zapisany na kurs."
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Kurs",
        help_text="Kurs, na który student się zapisuje."
    )

    class Meta:
        verbose_name = "Zapis na kurs"
        verbose_name_plural = "Zapisy na kursy"
        unique_together = ['student', 'course']
        ordering = ['-id']

    def __str__(self):
        return f"{self.student} - {self.course} ({self.get_status_display()})"
