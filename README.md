# Face Recognition Attendance System

## Overview
The Face Recognition Attendance System is a cutting-edge platform designed to automate attendance management in educational institutions. Using advanced face recognition technology, the system ensures accurate, secure, and efficient attendance recording while reducing manual effort and improving classroom operations.


## Key Features
- *Face Recognition*: Uses advanced algorithms to identify and verify students' faces for attendance.
- *Attendance Categorization*: Tracks and categorizes attendance as Present, Absent, or Late.
- *Email Notifications*: Admin or HOD sends attendance summaries to teachers, detailing student statuses.
- *User-Friendly Interface*: Simplifies attendance management with an intuitive design for students and teachers.
- *Scalability*: Built to handle large datasets, making it suitable for institutions of all sizes.
- *Future Enhancements*:
  - Mobile application integration for on-the-go access.
  - Detailed analytics and reports for attendance trends and insights.


## Technologies Used
- *Backend*: Django (Python)
- *Frontend*: HTML, CSS, JavaScript (Bootstrap for styling)
- *Face Recognition*: face_recognition library, OpenCV
- *Database*: MySQL
- *Email Integration*: Django Email Framework(SMTP)


## Installation

1. **Clone the repository**:
   ```bash 
   git clone https://github.com/ShyamTandel/FaceRecognitionAttendanceSystem.git
   cd FaceRecognitionAttendanceSystem

2. **Set up a virtual environment**:
   ```bash 
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Start your MySQL server (WAMP OR XAMPP)**:
   ```bash
   create a database name as attendance_db

5. **Change Email and App Password**:
   ```bash
   Here, we use SMTP for sending attendace mail
   1. Create an App password on google Email account
   2. Replace your Email and App password in Settings.py and admin.py file
   
6. **Apply migrations and run the server**:
   ```bash
   1. python manage.py makemigrations
   2. python manage.py migrate
   3. python manage.py runserver

7. **Access the application**:
   ```bash
   Open your browser and navigate to http://127.0.0.1:8000/
   
