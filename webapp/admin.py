from django.contrib import admin
from django_object_actions import DjangoObjectActions
from .models import *
from .CreateEncods import CreateEncods
from datetime import datetime
import os
import smtplib
import ssl
from email.message import EmailMessage

class stud_admin(DjangoObjectActions, admin.ModelAdmin):
    readonly_fields = ['image_tag']
    list_display = ['name', 'grade']
    ordering = ['name', 'grade']
    list_filter = ["grade"]

    def generate(modeladmin, request, queryset):
        encodings = CreateEncods()
        encodings.create_encodings(request)

    changelist_actions = ['generate']

class aten_admin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ["name", "grade", "status", "datetime"]
    list_filter = ["grade", "status", "datetime"]
    search_fields = ["name__name"]

    def initialize(self):
        self.choices = self.generate_choices()
        
        self.email_sender = 'dare16172@gmail.com'  # Your email address
        self.email_password = 'qddk oggq weco pddn'  # Use the app password
        self.smtp, self.email_sender = self.initiate_email()
        
        self.datetoday = datetime.now().date()
        self.sendEmails = {}
        self.nameList = []

        self.getLateStudents()
        self.getAbsentStudents()

    def generate_choices(self):
        choices = []

        for i in range(1,9):
            choices.extend([("P"+str(i)+"A", "Primary "+str(i)+"A"),
                            ("P"+str(i)+"B", "Primary "+str(i)+"B")])

        for i in range(9,11):
            choices.extend([("S"+str(i), "Secondary "+str(i))])

        for i in range(11,13):
            choices.extend([("PU"+str(i), "Pre-U "+str(i))])

        choices = tuple(choices)
        return choices

    def initiate_email(self):
        try:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()  
            smtp.login(self.email_sender, self.email_password)  # Ensure you've set this
            return smtp, self.email_sender
        except Exception as e:
            print(f"Error initiating email: {e}")
            return None, None


    def getClassObj(self, value):
        print(str(value))
        obj = None
        grade = None  # Initialize grade to avoid UnboundLocalError
        print(self.choices)
        for set in self.choices:
            if set[1] == str(value):
                grade = set[0]
                obj = classes.objects.get(grade=grade)
                break
        
        if obj is not None:
            return obj
        else:
            # Handle the case where obj is not found, or raise an exception
            raise ValueError(f"No class object found for grade: {value}")
    
    def getPresentStudents(self):
        records = attendance.objects.all()
        for record in records:
            # Check if the record is for today and the student is marked as present
            if record.datetime.date() == self.datetoday and record.status != "A" and record.status != 'L':
                self.nameList.append(str(record.name))  # Add the student's name to the list

                # Get the class object and form teacher's email
                obj = self.getClassObj(record.grade)
                email = obj.form_teacher

                # Initialize email entry for the form teacher if not already present
                if email not in self.sendEmails.keys():
                    self.sendEmails[email] = [[], [], []]  # Initialize with three lists

                # Add the present student to the third list
                time = record.datetime.strftime("%H:%M:%S")
                self.sendEmails[email][2].append(f'{record.name} : {time}')

    
    def getLateStudents(self):
        records = attendance.objects.all()
        for record in records:
            if record.datetime.date() == self.datetoday and record.status != "A" and record.status != "P" :
                self.nameList.append(str(record.name))
                obj = self.getClassObj(record.grade)

                email = obj.form_teacher
                
                if email not in self.sendEmails.keys():
                    self.sendEmails[email] = [[], [], []]
                
                if record.status == "L":
                    time = record.datetime.strftime("%H:%M:%S")                
                    
                    self.sendEmails[email][0].append(f'{record.name} : {time}')
                    
    def getAbsentStudents(self):
        def create_record(obj):
            # Create a new attendance record for an absent student
            record = attendance()
            record.name = obj
            record.grade = obj.grade
            record.status = "A"
            record.datetime = self.datetoday
            record.save()

        # Delete all previously created absent records for today
        attendance.objects.filter(status="A").delete()

        for obj in students.objects.all():
            try:
                # Check if the student already has a record for today
                existing_records = attendance.objects.filter(name=obj)

                # If no record exists, check for P or L status
                if not existing_records.exists():
                    # Check if the student has been marked as Present or Late
                    present_or_late_records = attendance.objects.filter(
                        name=obj,
                        datetime__date=self.datetoday,
                        status__in=["P", "L"]
                    )

                    # Only create an absent record if the student is not marked as Present or Late
                    if not present_or_late_records.exists():
                        create_record(obj)

                    # Add the absent student to the email list
                    if str(obj.name) not in self.nameList:
                        email = self.getClassObj(obj.grade).form_teacher

                        # Initialize teacher's email list if not present
                        if email not in self.sendEmails.keys():
                            self.sendEmails[email] = [[], [], []]

                        self.sendEmails[email][1].append(f'{obj.name}')
            except Exception as e:
                print(f"Error processing student {obj}: {e}")



 
    def send(self, request, queryset):
        print("in send......................................")
        self.initialize()

        if not self.smtp:  # Check if SMTP was initialized successfully
            print("SMTP connection failed, cannot send emails.")
            return
        
        self.getPresentStudents()
        
        for email_receiver, (late_students, absent_students, present_students) in self.sendEmails.items():
            try:
                grade = classes.objects.get(form_teacher=email_receiver).grade
            except classes.DoesNotExist:
                print(f"No class found for teacher: {email_receiver}")
                continue  

            subject = f'{self.datetoday} {grade} Attendance'

            em = EmailMessage()
            em['From'] = self.email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            
      

            body1 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(late_students))
            body2 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(absent_students))
            body3 = "<br>".join(f"{count + 1}. {student}" for count, student in enumerate(present_students))

            email_body = f'''
            <img src="https://ldce.ac.in/img/header.png" alt="LD College Of Engineering Header">
            <h1>{subject}</h1>
            <h2><u>Late Students</u></h2>
            <h3><i>{body1}</i></h3>
            <h2><u>Absent Students</u></h2>
            <h3><i>{body2}</i></h3>
            <h2><u>Present Students</u></h2>
            <h3><i>{body3}</i></h3>
            '''
          
        
            em.add_alternative(email_body, subtype='html')

            try:
                self.smtp.sendmail(self.email_sender, email_receiver, em.as_string())
                print(f"Email sent to {email_receiver}")
            except Exception as e:
                print(f"Failed to send email to {email_receiver}: {e}")
        self.smtp.quit() # Close the SMTP connection
    changelist_actions = ['send']



class div_admin(admin.ModelAdmin):
    list_display = ["ay", "division"]

admin.site.register(students, stud_admin)
admin.site.register(attendance, aten_admin)
admin.site.register(division, div_admin)
admin.site.register([academic_year, classes])
