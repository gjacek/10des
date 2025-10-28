# 10DEVS - Course Material Distribution Platform

A minimalist Django-based web application designed for instructors to easily and securely distribute course materials to students. The platform provides a simple, controlled environment for managing courses, lessons, and student enrollments.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Getting Started Locally](#getting-started-locally)
- [Available Scripts](#available-scripts)
- [Project Scope](#project-scope)
- [Project Status](#project-status)
- [License](#license)

## Tech Stack
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript (Server-rendered templates)
- **Database**: SQLite (for development), PostgreSQL (for production)

## Getting Started Locally

Follow these instructions to set up the project on your local machine for development and testing purposes.

### Prerequisites
- Python 3.x
- pip

### Installation
1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/10des.git
    cd 10des
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    *(Note: A `requirements.txt` file should be created for this step)*
    ```sh
    pip install -r requirements.txt 
    ```
    For now, you can install Django manually:
    ```sh
    pip install Django
    ```

4.  **Apply database migrations:**
    ```sh
    python manage.py migrate
    ```

5.  **Create a superuser account:**
    This account will have administrative privileges.
    ```sh
    python manage.py createsuperuser
    ```
    Follow the prompts to create your admin user.

6.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## Available Scripts

- `python manage.py runserver`: Starts the development server.
- `python manage.py migrate`: Applies changes to the database schema.
- `python manage.py createsuperuser`: Creates an administrator account.
- `python manage.py test`: Runs the test suite for the application.

## Project Scope

This project is an MVP focused on the core functionality of material distribution.

### Key Features
- **User Roles**:
    - **Student**: Can register, browse available courses, and request access. Once approved, can view lessons and download materials.
    - **Instructor**: Manages courses, lessons, and student enrollment requests. Instructor status is granted by an Administrator.
    - **Administrator**: Manages user roles (e.g., promoting a user to Instructor) via the Django Admin interface.
- **Course Management**: Instructors can create courses, add descriptions, and control their visibility (Visible/Hidden). Courses are not deleted but can be hidden.
- **Content Management**: Instructors can create lessons within courses, add file attachments, and set a lesson's status to "Published" or "Draft".
- **Enrollment System**: Access to courses is granted via a request/approve system. Students send a request to join, and the instructor can approve or reject it.
- **Secure File Access**: A dedicated endpoint verifies user permissions before serving file downloads, ensuring only enrolled students can access materials.

### Out of Scope (for MVP)
- Homework submissions and grading.
- Discussion forums, comments, or chat features.
- Quizzes and tests.
- Complex email notifications (beyond password reset).

## Project Status
**In Development**

The project is currently in the development phase of its Minimum Viable Product (MVP).

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
