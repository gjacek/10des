from django.core.management.base import BaseCommand
from django.utils import timezone
from kursy.models import CustomUser, Course, CourseEdition, Enrollment, Lesson

class Command(BaseCommand):
    help = 'Populates the database with test courses, editions, and enrollments.'

    def handle(self, *args, **options):
        self.stdout.write('Starting data population...')

        # 1. Users
        student, _ = CustomUser.objects.get_or_create(
            username='student@test.pl',
            defaults={
                'email': 'student@test.pl',
                'first_name': 'Jan',
                'last_name': 'Kowalski',
                'is_instructor': False
            }
        )
        if _:
            student.set_password('test123')
            student.save()
            self.stdout.write(f'Created student: {student}')
        else:
            self.stdout.write(f'Found student: {student}')

        instructor, _ = CustomUser.objects.get_or_create(
            username='instruktor@test.pl',
            defaults={
                'email': 'instruktor@test.pl',
                'first_name': 'Anna',
                'last_name': 'Nowak',
                'is_instructor': True
            }
        )
        if _:
            instructor.set_password('test123')
            instructor.save()
            self.stdout.write(f'Created instructor: {instructor}')
        else:
            self.stdout.write(f'Found instructor: {instructor}')

        # 2. Editions
        edition1, _ = CourseEdition.objects.get_or_create(name='Edycja 2024/Zima')
        edition2, _ = CourseEdition.objects.get_or_create(name='Edycja 2025/Wiosna')
        self.stdout.write('Created editions.')

        # 3. Courses
        course_python, _ = Course.objects.get_or_create(
            name='Podstawy Python',
            defaults={
                'description': 'Kompletny kurs programowania w języku Python od podstaw.',
                'is_visible': True,
                'instructor': instructor,
                'edition': edition1
            }
        )
        self.stdout.write(f'Created/Found course: {course_python.name}')

        course_django, _ = Course.objects.get_or_create(
            name='Zaawansowane Django',
            defaults={
                'description': 'Tworzenie skalowalnych aplikacji webowych w Django.',
                'is_visible': True,
                'instructor': instructor,
                'edition': edition2
            }
        )
        self.stdout.write(f'Created/Found course: {course_django.name}')
        
        course_hidden, _ = Course.objects.get_or_create(
            name='Tajny Projekt',
            defaults={
                'description': 'Kurs niewidoczny publicznie.',
                'is_visible': False,
                'instructor': instructor,
                'edition': edition1
            }
        )

        # 4. Enrollments
        # Student approved for Python
        Enrollment.objects.get_or_create(
            student=student,
            course=course_python,
            defaults={'status': 'approved'}
        )
        self.stdout.write(f'Enrolled {student} in {course_python} (approved)')

        # Student pending for Django
        Enrollment.objects.get_or_create(
            student=student,
            course=course_django,
            defaults={'status': 'pending'}
        )
        self.stdout.write(f'Enrolled {student} in {course_django} (pending)')
        
        # Student approved for Hidden (should be visible in My Courses if approved, even if course hidden? 
        # Plan says "Widok dostępny tylko dla zalogowanych studentów... status approved... Kursy widoczność... 
        # Course Detail plan says "Jeśli kurs jest ukryty -> 404 Not Found ... zgodnie z US-024, kurs znika z widoków studenta, nawet jeśli jest zapisany".
        # So we should test if this hidden course appears in My Courses. Logic in My Courses View currently only filters by enrollment status 'approved'.
        # It does NOT filter by course.is_visible. 
        # If the requirement is that hidden courses are NOT visible even if enrolled, we need to update the view.
        # Plan for My Courses doesn't explicitly mention is_visible check, only status approved.
        # But Course Detail says it should disappear. Consistency suggests it shouldn't be in the list either.
        # I will leave the view logic as is (based on plan) but add this data to verify behavior.
        Enrollment.objects.get_or_create(
            student=student,
            course=course_hidden,
            defaults={'status': 'approved'}
        )
        
        self.stdout.write(self.style.SUCCESS('Data population completed.'))

