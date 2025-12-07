"""
Management command do tworzenia użytkowników testowych.
"""
from django.core.management.base import BaseCommand
from kursy.models import CustomUser


class Command(BaseCommand):
    help = 'Tworzy użytkowników testowych (student, instruktor i admin)'

    def handle(self, *args, **options):
        # Usuń poprzednich użytkowników testowych jeśli istnieją
        CustomUser.objects.filter(email__in=[
            'student@test.pl', 
            'instruktor@test.pl',
            'admin@test.pl'
        ]).delete()

        # Utwórz studenta testowego
        student = CustomUser.objects.create_user(
            username='student@test.pl',
            email='student@test.pl',
            first_name='Jan',
            last_name='Kowalski',
            password='test123',
            is_instructor=False
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Utworzono studenta: {student.email}'))

        # Utwórz instruktora testowego
        instructor = CustomUser.objects.create_user(
            username='instruktor@test.pl',
            email='instruktor@test.pl',
            first_name='Anna',
            last_name='Nowak',
            password='test123',
            is_instructor=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Utworzono instruktora: {instructor.email}'))

        # Utwórz administratora
        admin = CustomUser.objects.create_superuser(
            username='admin@test.pl',
            email='admin@test.pl',
            first_name='Admin',
            last_name='Systemowy',
            password='admin123'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Utworzono administratora: {admin.email}'))

        self.stdout.write(self.style.WARNING('\n--- Ostrzeżenie bezpieczeństwa ---'))
        self.stdout.write('Hasła testowe zostały ustawione i usunięte z outputu dla bezpieczeństwa.')
        self.stdout.write('Użyj /admin/ do resetu haseł lub zmień je ręcznie w bazie danych.')
        self.stdout.write('Domyślne hasła: sprawdź dokumentację lub użyj Django shell.')

