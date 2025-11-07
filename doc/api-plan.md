# REST API Plan

## 1. Resources

The main resources are derived from the database entities and PRD requirements. Each resource corresponds to a table or a logical grouping:

- **Users**: Corresponds to `users_customuser` table. Handles user registration, login, roles (Student, Instructor, Admin).
- **CourseEditions**: Corresponds to `courses_courseedition` table. Manages course editions (e.g., semesters).
- **Courses**: Corresponds to `courses_course` table. Core resource for courses, including visibility and association with instructors and editions.
- **Lessons**: Corresponds to `courses_lesson` table. Lessons within courses, with publication status.
- **Attachments**: Corresponds to `courses_attachment` table. File attachments to lessons, with download tracking.
- **Enrollments**: Corresponds to `courses_enrollment` table. Manages student-course enrollments with status (pending, approved, rejected).

## 2. Endpoints

Endpoints are designed using RESTful principles, leveraging Django REST Framework (DRF) for serialization, authentication, and permissions. All endpoints require authentication except for public course views and registration/login. Use HTTPS for all.

### Users Resource

- **POST /api/auth/register/**
  - Description: Register a new user (Student by default).
  - Query Parameters: None.
  - Request JSON: 
    ```json
    {
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "password": "string"
    }
    ```
  - Response JSON: 
    ```json
    {
      "id": integer,
      "email": "string",
      "first_name": "string",
      "last_name": "string"
    }
    ```
  - Success: 201 Created - "User registered successfully."
  - Errors: 400 Bad Request - "Email already exists." or validation errors.

- **POST /api/auth/login/**
  - Description: Login user and return JWT token (assuming JWT auth).
  - Query Parameters: None.
  - Request JSON: 
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```
  - Response JSON: 
    ```json
    {
      "token": "string",
      "user": {
        "id": integer,
        "email": "string",
        "is_instructor": boolean
      }
    }
    ```
  - Success: 200 OK - "Login successful."
  - Errors: 401 Unauthorized - "Invalid credentials."

- **POST /api/auth/password-reset/**
  - Description: Request password reset via email.
  - Query Parameters: None.
  - Request JSON: 
    ```json
    {
      "email": "string"
    }
    ```
  - Response JSON: 
    ```json
    {
      "message": "Reset email sent."
    }
    ```
  - Success: 200 OK.
  - Errors: 400 Bad Request - "Email not found." (generic message for security).

- **GET /api/users/me/**
  - Description: Get current user profile.
  - Query Parameters: None.
  - Response JSON: User details as above.
  - Success: 200 OK.
  - Errors: 401 Unauthorized.

- **PUT /api/users/me/**
  - Description: Update user profile (Admin can update roles).
  - Query Parameters: None.
  - Request JSON: Partial user fields.
  - Response JSON: Updated user.
  - Success: 200 OK.
  - Errors: 403 Forbidden - If not authorized to update roles.

### CourseEditions Resource

- **GET /api/course-editions/**
  - Description: List all course editions (paginated).
  - Query Parameters: `page=integer`, `search=string` (filter by name).
  - Response JSON: 
    ```json
    {
      "count": integer,
      "next": "url",
      "previous": "url",
      "results": [
        {
          "id": integer,
          "name": "string"
        }
      ]
    }
    ```
  - Success: 200 OK.
  - Errors: None specific.

- **POST /api/course-editions/**
  - Description: Create a new course edition (Admin/Instructor only).
  - Request JSON: 
    ```json
    {
      "name": "string"
    }
    ```
  - Response JSON: Created edition.
  - Success: 201 Created.
  - Errors: 400 Bad Request - "Name must be unique."

- **GET /api/course-editions/{id}/**
  - Description: Retrieve a specific edition.
  - Response JSON: Edition details.
  - Success: 200 OK.
  - Errors: 404 Not Found.

- **PUT /api/course-editions/{id}/**
  - Description: Update edition (Admin only).
  - Request JSON: Partial fields.
  - Success: 200 OK.
  - Errors: 403 Forbidden.

- **DELETE /api/course-editions/{id}/**
  - Description: Delete edition (if no courses associated, Admin only).
  - Success: 204 No Content.
  - Errors: 403 Forbidden - "Cannot delete edition with associated courses."

### Courses Resource

- **GET /api/courses/**
  - Description: List public/visible courses (for students/guests). Authenticated users see enrollable courses.
  - Query Parameters: `page=integer`, `edition_id=integer` (filter), `search=string` (name/description), `is_visible=true/false`.
  - Response JSON: Paginated list with:
    ```json
    {
      "id": integer,
      "name": "string",
      "description": "string",
      "is_visible": boolean,
      "instructor": {
        "id": integer,
        "first_name": "string",
        "last_name": "string",
        "email": "string"
      },
      "edition": {
        "id": integer,
        "name": "string"
      }
    }
    ```
  - Success: 200 OK.
  - Errors: None.

- **GET /api/courses/{id}/**
  - Description: Retrieve course details (public info if visible, full if enrolled/instructor).
  - Response JSON: Full course with lessons summary if authorized.
  - Success: 200 OK.
  - Errors: 404 Not Found or 403 Forbidden if not authorized.

- **POST /api/courses/**
  - Description: Create a new course (Instructor only).
  - Request JSON: 
    ```json
    {
      "name": "string",
      "description": "string",
      "is_visible": boolean (default false),
      "edition_id": integer
    }
    ```
  - Response JSON: Created course.
  - Success: 201 Created.
  - Errors: 400 Bad Request - Validation errors.

- **PUT /api/courses/{id}/**
  - Description: Update course (Instructor/Owner only). Includes toggling visibility.
  - Request JSON: Partial fields.
  - Success: 200 OK.
  - Errors: 403 Forbidden.

- **POST /api/courses/{id}/enroll/**
  - Description: Request enrollment (Student only, if not already enrolled/rejected).
  - Request JSON: Empty or {"notes": "string"}.
  - Response JSON: 
    ```json
    {
      "message": "Enrollment request sent.",
      "status": "pending"
    }
    ```
  - Success: 201 Created.
  - Errors: 400 Bad Request - "Already enrolled or rejected."

### Lessons Resource

- **GET /api/courses/{course_id}/lessons/**
  - Description: List lessons for a course (published only for students, all for instructor).
  - Query Parameters: `page=integer`, `is_published=true/false` (instructor filter), `ordering=title` (default alphabetical).
  - Response JSON: Paginated list:
    ```json
    {
      "id": integer,
      "title": "string",
      "description": "string",
      "is_published": boolean
    }
    ```
  - Success: 200 OK.
  - Errors: 403 Forbidden if not authorized.

- **GET /api/courses/{course_id}/lessons/{id}/**
  - Description: Retrieve lesson details (published only for students).
  - Response JSON: Lesson with attachments list if authorized.
  - Success: 200 OK.
  - Errors: 403/404.

- **POST /api/courses/{course_id}/lessons/**
  - Description: Create lesson (Instructor of course only).
  - Request JSON: 
    ```json
    {
      "title": "string",
      "description": "string",
      "is_published": boolean (default false)
    }
    ```
  - Success: 201 Created.
  - Errors: 403/400.

- **PUT /api/courses/{course_id}/lessons/{id}/**
  - Description: Update lesson, including toggle publication.
  - Request JSON: Partial.
  - Success: 200 OK.
  - Errors: 403.

- **DELETE /api/courses/{course_id}/lessons/{id}/**
  - Description: Delete lesson (Instructor only).
  - Success: 204.
  - Errors: 403.

### Attachments Resource

- **GET /api/courses/{course_id}/lessons/{lesson_id}/attachments/**
  - Description: List attachments for a lesson (authorized users only).
  - Query Parameters: `page=integer`.
  - Response JSON: 
    ```json
    {
      "id": integer,
      "original_filename": "string",
      "download_count": integer,
      "file_url": "string" (signed URL)
    }
    ```
  - Success: 200 OK.
  - Errors: 403.

- **POST /api/courses/{course_id}/lessons/{lesson_id}/attachments/**
  - Description: Upload attachment (Instructor only). Multipart form with file.
  - Request: Multipart - `file` (up to 10MB, allowed extensions: pdf,zip,pptx,docx,txt,jpg,jpeg).
  - Response JSON: Created attachment.
  - Success: 201 Created.
  - Errors: 400 - "Invalid file type/size" or "Max 10 attachments per lesson."

- **GET /api/attachments/{id}/download/**
  - Description: Download attachment (increments count). Returns file stream.
  - Response: Binary file.
  - Success: 200 OK.
  - Errors: 403 Forbidden.

- **DELETE /api/courses/{course_id}/lessons/{lesson_id}/attachments/{id}/**
  - Description: Delete attachment (Instructor only).
  - Success: 204.
  - Errors: 403.

### Enrollments Resource

- **GET /api/courses/{course_id}/enrollments/**
  - Description: List enrollments for course (Instructor only). Filtered by status.
  - Query Parameters: `status=pending|approved|rejected`, `page=integer`.
  - Response JSON: Paginated:
    ```json
    {
      "id": integer,
      "status": "string",
      "student": {
        "id": integer,
        "first_name": "string",
        "last_name": "string",
        "email": "string"
      }
    }
    ```
  - Success: 200 OK.
  - Errors: 403.

- **POST /api/courses/{course_id}/enrollments/{enrollment_id}/approve/**
  - Description: Approve pending enrollment (Instructor only).
  - Request JSON: Empty.
  - Response JSON: {"message": "Approved.", "status": "approved"}
  - Success: 200 OK.
  - Errors: 400 - "Not pending."

- **POST /api/courses/{course_id}/enrollments/{enrollment_id}/reject/**
  - Description: Reject enrollment (Instructor only).
  - Success: 200 OK - Status to "rejected".

- **POST /api/courses/{course_id}/enrollments/{enrollment_id}/restore/**
  - Description: Restore rejected to approved (Instructor only).
  - Success: 200 OK.

- **DELETE /api/courses/{course_id}/enrollments/{enrollment_id}/**
  - Description: Remove approved enrollment (Instructor only).
  - Success: 204.
  - Errors: 400 - "Cannot remove non-approved."

- **GET /api/users/me/enrollments/**
  - Description: List user's enrollments (Student only, approved courses).
  - Query Parameters: `status=approved`.
  - Response: List of courses user is enrolled in.
  - Success: 200 OK.

## 3. Authentication and Authorization

- **Mechanism**: JWT (JSON Web Tokens) using Django REST Framework's JWT addon or djangorestframework-simplejwt. Tokens obtained on login, included in Authorization header: `Bearer <token>`.
- **Implementation Details**:
  - Public endpoints (e.g., GET /api/courses/) allow anonymous access for visible courses.
  - Protected endpoints use DRF permissions: IsAuthenticated for general access, IsInstructor (custom permission checking is_instructor and ownership) for course/lesson management.
  - Admin endpoints use IsAdminUser.
  - Rate limiting: DRF throttling (AnonRateThrottle for public, UserRateThrottle for authenticated).
  - CSRF: Exempt for API (stateless), but enable for session-based if needed.
  - Security: All sensitive data (passwords) hashed; email unique; roles enforced via permissions.

## 4. Validation and Business Logic

- **Validation Conditions** (from DB schema):
  - Users: Email unique, required first_name/last_name, password hashed. is_instructor default False.
  - CourseEditions: Name unique, not null.
  - Courses: Name/description not null, is_visible default False, foreign keys to instructor/edition (ON DELETE PROTECT).
  - Lessons: Title/description not null, is_published default False, foreign key to course (ON DELETE CASCADE).
  - Attachments: File path/original_filename not null, download_count default 0, foreign key to lesson (ON DELETE CASCADE), max 10 per lesson, 10MB size, allowed extensions.
  - Enrollments: Status default 'pending', unique (student, course), foreign keys (ON DELETE CASCADE).

  Implemented via DRF serializers with validators (e.g., UniqueValidator, MaxLengthValidator, FileExtensionValidator, FileSizeValidator).

- **Business Logic Implementation**:
  - Enrollment workflow: POST /enroll/ creates pending enrollment if not exists/rejected. Approve/Reject/Restore updates status and triggers signals (e.g., hide courses on instructor deactivation via post_save signal on User).
  - Visibility: GET endpoints filter by is_visible=True for public; for enrolled users, show regardless if approved.
  - Publication: Lessons filtered by is_published=True for students.
  - File handling: Use Django's FileField/Media for storage; signed URLs for downloads; increment download_count on GET /download/.
  - Auto-hide courses: On User update (is_active=False for instructor), signal sets is_visible=False on their courses.
  - Sorting: Default ordering=['title'] on Lesson queryset.
  - Pagination: DRF's PageNumberPagination (default page_size=20).
  - Filtering/Search: Use django-filter for query params.
  - Metrics: Download count auto-incremented; log enrollments via signals or audit logs.
  - Assumptions: No rate limiting specifics beyond DRF defaults; email for reset uses Django's built-in; no real-time (use polling if needed).
