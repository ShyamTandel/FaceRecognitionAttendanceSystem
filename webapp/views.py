from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .CreateEncods import CreateEncods
from .aten_monitor import aten_monitor
from django.contrib import messages, admin
from django.http import JsonResponse
from django.utils import timezone 
from .admin import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from datetime import timedelta
from django.utils.timezone import localtime


def home(request):
    if request.user_agent.is_pc:
        return render(request, 'home.html')
    else:
        return redirect('admin:index')
    
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'baseadmin.html'
    login_url = 'admin_login'
    
class AdminLoginView(LoginView):
    template_name = 'admin_login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('admin_dashboard')
    
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:  # Check if user is admin
            login(request, user)
            return redirect('attendance')  # Redirect to admin dashboard after login
        else:
            messages.error(request, "Invalid credentials or unauthorized access.")
    return render(request, 'admin_login.html')
    
    

def app(request):
    if request.user_agent.is_pc:
        return render(request, 'app.html')
    else:
        return redirect('admin:index')
    
    
    
    

def stream(request):
    if request.user_agent.is_pc:
        profiles = students.objects.all()
        if len(profiles) > 0:
            encodings = CreateEncods()
            encodings.create_encodings(request)
            if not encodings.error_message:
                monitoring = aten_monitor()
                monitoring.start()
        else:
            messages.warning(request, 'Please Create At Least One Student Profile Before Continuing!')

        return render(request, 'stream.html')
    else:
        return redirect('admin:index')





def indexadmin(request):
    return render(request, 'indexadmin.html')






def academic_year_view(request):
    # Fetch academic years at the beginning
    academic_years = academic_year.objects.all()
    
    def format_year(selected_year):
        # Format the year for the error message
        start_year = '20' + str(selected_year)[:2]  # Assuming the year is in '2223' format
        end_year = '20' + str(selected_year)[2:]
        formatted_year = f"{start_year}-{end_year}"
        return formatted_year

    if request.method == 'POST':
        # Check for academic year edit first
        if 'edit_id' in request.POST:  # Prioritize edit logic over addition
            year_id = request.POST.get('edit_id')
            selected_year = request.POST.get('academic_year')
            year_instance = get_object_or_404(academic_year, id=year_id)
            
            # Check if the selected year is different from the current year
            if academic_year.objects.filter(year=selected_year).exists():
                messages.info(request, "No changes made to the academic year.")  # Inform the user that no change occurred.
            elif year_instance.year != selected_year:
                old_year = year_instance.year
                year_instance.year = selected_year
                year_instance.save()
                messages.success(request, f"Academic year {format_year(old_year)} has been successfully updated to {format_year(selected_year)}.")
            return redirect('academic_year')  # Redirect after editing


        # Check for academic year addition
        elif 'academic_year' in request.POST:  # This block only handles new year addition
            selected_year = request.POST.get('academic_year')
            
            # Check if the selected year already exists
            if academic_year.objects.filter(year=selected_year).exists():
                messages.info(request, f"Academic year {format_year(selected_year)} already exists. No changes made.")
                return redirect('academic_year')  # Redirect back to the same page
            else:
                messages.success(request, f"Academic year {format_year(selected_year)} has been added successfully.")
            
            if selected_year:  # Check if a year was selected
                # Create a new academic_year instance and save it to the database
                new_academic_year = academic_year(year=selected_year)
                new_academic_year.save()
                return redirect('academic_year')  # Redirect to the same page
            
            

        # Check for academic year deletion
        elif 'delete_id' in request.POST:
            year_id = request.POST.get('delete_id')
            year_instance = get_object_or_404(academic_year, id=year_id)
            year_to_delete = year_instance.year  # Store the formatted year
            year_instance.delete()
            messages.success(request, f"Academic year {format_year(year_to_delete)} has been deleted successfully.")
            return redirect('academic_year')  # Redirect after deletion



    # Format the years after fetching them from the database
    formatted_years = []
    for year in academic_years:
        start_year = '20' + str(year.year)[:2]  # Assuming the year is in '2223' format
        end_year = '20' + str(year.year)[2:]
        formatted_years.append({
            'formatted_year': f"{start_year}-{end_year}",
            'id': year.id
        })
        

    return render(request, 'academic_year.html', {
        'academic_years': formatted_years,  # Use formatted years in the template
        'academic_year': academic_year,  # Pass the model to access choices
    })






def division_view(request):
    if request.method == 'POST':
        # Handle adding or editing a division
        academic_year_id = request.POST.get('academic_year')
        division_choice = request.POST.get('division')
        edit_id = request.POST.get('edit_id')  # Retrieve edit_id from the form

        # Handle delete functionality
        if 'delete_id' in request.POST:
            division_id = request.POST.get('delete_id')
            division_instance = get_object_or_404(division, id=division_id)
            division_name = division_instance.get_division_display()
            ay_instance = division_instance.ay

            # Delete the division
            division_instance.delete()
            messages.success(request, f"Division '{division_name}, {ay_instance}' has been deleted successfully.")
            return redirect('division')

        # Handle edit functionality (only if edit_id is not empty)
        elif edit_id:
            division_instance = get_object_or_404(division, id=edit_id)
            
            old_division_instance = division_instance.get_division_display()
            old_ay_instance = division_instance.ay

            if academic_year_id and division_choice:
                ay_instance = get_object_or_404(academic_year, id=academic_year_id)

                # Check if a different division with the same values exists
                if division.objects.filter(ay=ay_instance, division=division_choice).exists():
                    messages.info(request, "This division already exists for the selected academic year. No changes made.")
                else:
                    division_instance.ay = ay_instance
                    division_instance.division = division_choice
                    division_instance.save()
                    messages.success(request, f"Division '{old_division_instance}, {old_ay_instance}' has been updated successfully to '{division_instance}, {ay_instance}'.")
                return redirect('division')

        # Handle adding a new division (when edit_id is not provided)
        else:
            if academic_year_id and division_choice:
                ay_instance = get_object_or_404(academic_year, id=academic_year_id)

                # Check if the division already exists
                if division.objects.filter(ay=ay_instance, division=division_choice).exists():
                    messages.info(request, "This division already exists for the selected academic year. No changes made.")
                else:
                    new_division = division(ay=ay_instance, division=division_choice)
                    new_division.save()
                    messages.success(request, f"Division '{new_division.get_division_display()}, {ay_instance}' has been added successfully.")
            return redirect('division')

    # Fetch all academic years and existing divisions
    academic_years = academic_year.objects.all()  # Query all academic years
    division_choices = division.choices  # Fetch division choices from the model
    divisions = division.objects.all()  # Fetch existing division records

    return render(request, 'division.html', {
        'academic_years': academic_years,
        'division_choices': division_choices,
        'divisions': divisions,
    })









def classes_view(request):
    # Fetch all divisions and grade choices from the model dynamically
    divisions = division.objects.all()  # Query all divisions
    grades = list(classes.choices)  # Fetch grade choices from the model
    classes_list = classes.objects.all()  # Fetch existing class records

    if request.method == 'POST':
        division_id = request.POST.get('division')  # Division from the dropdown
        grade_choice = request.POST.get('grade')  # Grade from the dropdown
        form_teacher = request.POST.get('form_teacher')  # Teacher email
        edit_id = request.POST.get('edit_id')  # Retrieve edit_id for editing

        # Handle delete functionality
        if 'delete_id' in request.POST:
            class_id = request.POST.get('delete_id')
            class_instance = get_object_or_404(classes, id=class_id)

            class_name = class_instance.get_grade_display()  # Assuming you want grade displayed
            division_instance = class_instance.div

            # Delete the class
            class_instance.delete()
            messages.success(request, f"Class '{class_name}, {division_instance}' has been deleted successfully.")
            return redirect('classes')

        # Handle edit functionality
        elif edit_id:
            class_instance = get_object_or_404(classes, id=edit_id)
            old_grade = class_instance.get_grade_display()
            old_division = class_instance.div

            if division_id and grade_choice and form_teacher:
                division_instance = get_object_or_404(division, id=division_id)

                # Check if another class with the same values exists
                if classes.objects.filter(div=division_instance, grade=grade_choice).exists():
                    messages.info(request, "This class already exists for the selected division. No changes made.")
                else:
                    class_instance.div = division_instance
                    class_instance.grade = grade_choice
                    class_instance.form_teacher = form_teacher
                    class_instance.save()
                    messages.success(request, f"Class '{old_grade}, {old_division}' has been updated successfully to '{class_instance.get_grade_display()}, {division_instance}'.")
                return redirect('classes')

        # Handle adding a new class
        else:
            if division_id and grade_choice and form_teacher:
                division_instance = get_object_or_404(division, id=division_id)

                # Check if the class already exists
                if classes.objects.filter(div=division_instance, grade=grade_choice).exists():
                    messages.info(request, "This class already exists for the selected division. No changes made.")
                else:
                    new_class = classes(div=division_instance, grade=grade_choice, form_teacher=form_teacher)
                    new_class.save()
                    messages.success(request, f"Class '{new_class.get_grade_display()}, {division_instance.ay}, {division_instance.get_division_display()}' has been added successfully.")
            return redirect('classes')

    # Fetch the choices for grades from the model dynamically for the dropdown
    grade_choices = classes.choices

    return render(request, 'classes.html', {
        'divisions': divisions,
        'grades': grade_choices,  # Dynamically generated choices passed to the template
        'classes_list': classes_list,
    })
    





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import students, classes  # Assuming the 'classes' model is for grades

def students_view(request):
    if request.method == 'POST':
        # Handle adding or editing a student
        name = request.POST.get('name')
        grade_id = request.POST.get('grade')
        edit_id = request.POST.get('edit_id')

        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')

        if 'delete_id' in request.POST:
            # Handle delete functionality
            student_id = request.POST.get('delete_id')
            student_instance = get_object_or_404(students, id=student_id)
            student_instance.delete()
            messages.success(request, "Student has been deleted successfully.")
            return redirect('students')

        if edit_id:
            # Edit existing student
            student_instance = get_object_or_404(students, id=edit_id)
            student_instance.name = name
            student_instance.grade_id = grade_id
            if photo1:
                student_instance.photo1 = photo1
            if photo2:
                student_instance.photo2 = photo2
            if photo3:
                student_instance.photo3 = photo3
            student_instance.save()
            messages.success(request, "Student has been updated successfully.")
        else:
            # Add a new student
            new_student = students(name=name, grade_id=grade_id, photo1=photo1, photo2=photo2, photo3=photo3)
            new_student.save()
            messages.success(request, "Student has been added successfully.")

        return redirect('students')

    # Fetch all students and grades
    students_list = students.objects.all()
    grades = classes.objects.all()

    return render(request, 'students.html', {
        'students': students_list,
        'grades': grades,
    })




def attendance_view(request):
    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        student_id = request.POST.get("name")
        grade_id = request.POST.get("grade")
        status = request.POST.get("status")

        print(f"Received Data: edit_id={edit_id}, student_id={student_id}, grade_id={grade_id}, status={status}")

    # Handle delete request
    if request.method == "POST" and "delete_id" in request.POST:
        delete_id = request.POST.get("delete_id")
        if delete_id:
            try:
                record_to_delete = attendance.objects.get(id=delete_id)
                record_to_delete.delete()  # Delete the record
                messages.success(request, "Attendance record deleted successfully.")
            except attendance.DoesNotExist:
                messages.error(request, "Attendance record not found.")

        return redirect("attendance")  # Redirect to the attendance page


    # Fetch attendance records, students, and classes
    attendance_records = attendance.objects.all()
    
    for record in attendance_records:
        record.adjusted_datetime = record.datetime - timedelta(hours=5, minutes=30)
        if record.status == "A":
            adjusted_datetime = datetime.now().date()
            record.adjusted_datetime = adjusted_datetime.strftime("%b. %d, %Y").replace(' 0',' ')  # Date only
        # else:
        #     adjusted_time = datetime.now()
        #     record.formatted_datetime = adjusted_time.strftime("%Y-%m-%d %H:%M:%S")
    students_list = students.objects.all()
    grades_list = classes.objects.all()
    status_choices = attendance.choices

    return render(request, "attendance.html", {
        "attendance": attendance_records,
        "students": students_list,
        "grades": grades_list,
        "status_choices": status_choices,
    })




def send_attendance_email(request):
    if request.method == "POST":
        try:
            # Initialize the aten_admin with the admin site and model
            admin_instance = aten_admin(attendance, admin.site)
            admin_instance.send(request, None)  # Call the send method defined in aten_admin
            messages.success(request, "Attendance emails sent successfully.")
        except Exception as e:
            messages.error(request, f"Error sending emails: {str(e)}")
    
    return redirect('attendance')


def send_email_to_teachers(request):
    if request.method == "POST":
        selected_teachers = request.POST.getlist("selected_teachers")
        
        if not selected_teachers:
            messages.error(request, "Please select at least one teacher.")
            return redirect("attendance")

        # Initialize the aten_admin class to get the attendance info
        aten_admin_instance = aten_admin()
        aten_admin_instance.initialize()

        smtp = aten_admin_instance.smtp
        email_sender = aten_admin_instance.email_sender

        if not smtp:
            messages.error(request, "Failed to connect to email server.")
            return redirect("attendance")
        
        for email_receiver in selected_teachers:
            if email_receiver in aten_admin_instance.sendEmails:
                late_students, absent_students, present_students = aten_admin_instance.sendEmails[email_receiver]

                try:
                    # Fetch the grade for the teacher
                    grade = classes.objects.get(form_teacher=email_receiver).grade
                except classes.DoesNotExist:
                    messages.error(request, f"No class found for teacher: {email_receiver}")
                    continue

                # # Query Present Students
                # present_students = attendance.objects.filter(
                #     student__class__form_teacher=email_receiver,
                #     status="Present"
                # ).values_list('student__name', flat=True)

                # Format Lists
                body1 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(late_students))
                body2 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(absent_students))
                body3 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(present_students))

                # Email Subject and Body
                subject = f'{aten_admin_instance.datetoday} {grade} Attendance'

                email_body = f'''
                <img src="https://ldce.ac.in/img/header.png" alt="LD College Of Engineering Header">
                <h1>{subject}</h1>
                <h2><u>Present Students</u></h2>
                <h3><i>{body3}</i></h3>
                <h2><u>Late Students</u></h2>
                <h3><i>{body1}</i></h3>
                <h2><u>Absent Students</u></h2>
                <h3><i>{body2}</i></h3>
                '''
                
                # Prepare and Send Email
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.add_alternative(email_body, subtype='html')

                try:
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
                    print(f"Email sent to {email_receiver}")
                except Exception as e:
                    print(f"Failed to send email to {email_receiver}: {e}")

        smtp.quit()
        messages.success(request, "Emails sent successfully.")
        return redirect("attendance")
