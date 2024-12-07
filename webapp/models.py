from django.db import models
from django.utils.html import mark_safe
import os
import urllib
import numpy as np
import cv2
import imutils
import face_recognition
from fr_as.settings import MEDIA_ROOT
# Create your models here.

class Rename:
    def __init__(self, number):
        self.number = number

    def save(self, instance, filename):
        instance = str(instance)
        alphabet = instance[0].upper()
        newpath = os.path.join(MEDIA_ROOT, alphabet)

        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        ext = os.path.splitext(filename)[1]
        filename = f"{instance}{self.number}{ext}"
        return os.path.join(alphabet, filename)

class academic_year(models.Model):
    choices = (
        ("2223", "2022-2023"),
        ("2324", "2023-2024"),
        ("2425", "2024-2025"),
        ("2526", "2025-2026"),
        ("2627", "2026-2027"),
    )
    year = models.CharField(max_length=9, choices=choices)

    def __str__(self):
        for set in self.choices:
            if set[0] == self.year:
                return set[1]

class division(models.Model):
    choices = (
        ("Pri", "Primary"),
        ("Sec", "Secondary"),
        ("Pre-U", "Pre-University"),
    )

    ay = models.ForeignKey(academic_year, on_delete=models.CASCADE)
    division = models.CharField(max_length=14, choices=choices)

    def __str__(self):
        for set in self.choices:
            if set[0] == self.division:
                return set[1]

class classes(models.Model):
    choices = []

    for i in range(1,9):
        choices.extend([("P"+str(i)+"A", "Primary "+str(i)+"A"),
                        ("P"+str(i)+"B", "Primary "+str(i)+"B")])

    for i in range(9,11):
        choices.extend([("S"+str(i), "Secondary "+str(i))])

    for i in range(11,13):
        choices.extend([("PU"+str(i), "Pre-U "+str(i))])

    choices = tuple(choices)

    div = models.ForeignKey(division, on_delete=models.CASCADE)
    grade = models.CharField(max_length=4, choices=choices)
    form_teacher = models.EmailField()

    def __str__(self):
        for set in self.choices:
            if set[0] == self.grade:
                return set[1]

class students(models.Model):
    name = models.CharField(max_length=50)
    grade = models.ForeignKey(classes, on_delete=models.CASCADE)

    photo1 = models.ImageField(upload_to=Rename(1).save, max_length=300)
    photo2 = models.ImageField(upload_to=Rename(2).save, blank=True, max_length=300)
    photo3 = models.ImageField(upload_to=Rename(3).save, blank=True, max_length=300)
    
    encoding1 = models.BinaryField(blank=True, null=True, editable=False)
    encoding2 = models.BinaryField(blank=True, null=True, editable=False)
    encoding3 = models.BinaryField(blank=True, null=True, editable=False)

    photoUI = models.ImageField(editable=False, blank=True, max_length=300)

    def fetch_img(self):
        local_host = 'http://127.0.0.1:8000'
        image_url = local_host + self.photo1.url
        resp = urllib.request.urlopen(image_url)
        arr = np.asarray(bytearray(resp.read()), dtype="uint8")
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img

    def set_filepath(self):
        path = os.path.join(MEDIA_ROOT, 'PhotoUI')
        filename = self.name + '_PhotoUI.jpg'
        abs_path = os.path.join(path, filename)
        rel_path = os.path.join('PhotoUI', filename)
        return abs_path, rel_path

    def insert_text(self, img, filepath, text):
        image = imutils.resize(img, width=200)
        cv2.putText(image,text,(0, int(image.shape[0]/2)),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        cv2.imwrite(filepath, image)
    
    def image_tag(self):
        if self.photo1:
            img = self.fetch_img()
            abs_path, rel_path = self.set_filepath()
            resized_img = imutils.resize(img, width=500)
            faceLocList = face_recognition.face_locations(resized_img)

            if len(faceLocList) == 1:
                faceLoc = faceLocList[0]
                y1,x2,y2,x1 = faceLoc
                cropped_img = resized_img[y1:y2, x1:x2]

                face_img = imutils.resize(cropped_img, width=200)
                cv2.imwrite(abs_path, face_img)

            elif len(faceLocList) > 1:
                text = 'MANY FACES'
                self.insert_text(resized_img, abs_path, text)
            
            else:
                text = 'NO FACE'
                self.insert_text(resized_img, abs_path, text)

            self.photoUI = rel_path
            self.save()

        return mark_safe(f'<img src="{self.photoUI.url}"/>')

    image_tag.short_description = 'Face'

    def save(self, *args, **kwargs):
        try:
            obj = students.objects.get(pk=self.pk)
        except students.DoesNotExist:
            pass 
        else:
            if not obj.photo1 == self.photo1: 
                self.encoding1 = b''
            if not obj.photo2 == self.photo2: 
                self.encoding2 = b''
            if not obj.photo3 == self.photo3: 
                self.encoding3 = b''
        super(students, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class attendance(models.Model):
    choices = (
        ("P", "Present"),
        ("A", "Absent"),
        ("L", "Late"),
    )

    name = models.ForeignKey(students, on_delete=models.CASCADE)
    grade = models.ForeignKey(classes, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=choices, default="A")
    datetime = models.DateTimeField()

    def __str__(self):
        return str(self.name)
