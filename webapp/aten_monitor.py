import cv2
import face_recognition
import numpy as np
from .TakeAttendance import TakeAttendance
import datetime

class aten_monitor(TakeAttendance):
    def __init__(self):
        super().__init__()
        self.status_key = {"L": "Late", "P": "Present", "A": "Absent"}
        self.color = (0, 0, 255)  # Red for unknown or absent
        self.cap = cv2.VideoCapture(0)

    def start(self):
        while True:
            _, img = self.cap.read()

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)
                
                if faceDis[matchIndex] < 0.50:
                    name_class = self.classNames[matchIndex]
                    name, grade = name_class.split('(')[0].strip(), name_class.split('(')[1][:-1]
                    result = self.markAttendance(name)
                    
                    # Debugging logs to check time-based status
                    print(f"Time now: {datetime.datetime.now().time()}")
                    print(f"Attendance status: {self.status_key[result[0]]}, Time: {result[1].strftime('%H:%M:%S')}")

                    # Get the attendance status based on the time intervals
                    status = self.status_key[result[0]]
                    time = result[1].strftime("%H:%M:%S")

                    fname = name.split(' ')[0]
                    label = fname + f' ({grade})'
                    
                    # Determine color based on attendance status
                    if status == "Present":
                        self.color = (0, 255, 0)  # Green for present
                    elif status == "Late":
                        self.color = (0, 255, 255)  # Yellow for late
                    else:
                        self.color = (0, 0, 255)  # Red for absent
                    
                    # Draw the attendance status on the image
                    coor1 = (150, img.shape[0] - 75)
                    coor2 = (430, img.shape[0] - 50)
                    cv2.rectangle(img, coor1, coor2, self.color, cv2.FILLED)
                    cv2.putText(img, status + " " + time, (150, img.shape[0] - 50),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                else: 
                    label = 'Unknown'
                
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), self.color, 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), self.color, cv2.FILLED)
                cv2.putText(img, label, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow('Webcam', img)
            
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def markAttendance(self, name):
        obj = self.run_query(f'''
            SELECT id, grade_id FROM webapp_students
            WHERE name = '{name}'
        ''')

        name_grade = obj.fetchone()

        if name not in self.nameList and name_grade:  # Ensure name_grade is valid
            self.nameList.append(name)
            current = datetime.datetime.now()
            current_time = current.time()

            # Debugging logs to check the time being processed
            print(f"Current time: {current_time}")

            # Define the time ranges for attendance marking
            time_present_start = datetime.time(10, 30, 0)
            time_present_end = datetime.time(13, 0, 0)
            # time_late_start = datetime.time(13, 0, 1)
            # time_late_end = datetime.time(17, 0, 0)

            # Mark attendance based on the time range
            if time_present_start <= current_time <= time_present_end:
                status = 'P'  # Present
            # elif time_late_start <= current_time <= time_late_end:
            #     status = 'L'  # Late
            else:
                status = 'L'  # Absent converted to Late
            # Debugging log to check the chosen status
            print(f"Status after time check: {status}")

            # Insert attendance record into the database
            self.run_query(f'''
                INSERT INTO webapp_attendance (status, datetime, grade_id, name_id)
                VALUES ('{status}', '{current}', {name_grade[1]}, {name_grade[0]})
            ''')

        # Use DATE() to extract the date in MySQL
        obj2 = self.run_query(f'''
                        SELECT status, datetime FROM webapp_attendance
                        WHERE DATE(datetime) = CURDATE() AND name_id = {name_grade[0]}
                        ''')

        return obj2.fetchone()