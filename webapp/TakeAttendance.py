import datetime
from django.db import connection
import pickle
import base64


class TakeAttendance:
    def __init__(self):
        self.late = datetime.time(7, 30, 0)

        self.fetch_encods()
        self.nameList = self.getNameList()

    def run_query(self, query):
        cursor = connection.cursor()
        cursor.execute(query)

        return cursor

    def convert(self, encoding):
        np_bytes = base64.b64decode(encoding)
        np_array = pickle.loads(np_bytes)
        self.encodeListKnown.append(np_array)
        self.classNames.append(self.label)

    def fetch_encods(self):
        record_list = self.run_query('''
        SELECT * FROM webapp_students
        ''').fetchall()

        self.classNames = []
        self.encodeListKnown = []

        for i in range(len(record_list)):
            obj = self.run_query(f'''
            SELECT grade FROM webapp_classes
            WHERE id = {record_list[i][9]}
            ''')
            self.label = record_list[i][1] + f' ({obj.fetchone()[0]})'
            
            encoding1 = record_list[i][5]
            encoding2 = record_list[i][6]
            encoding3 = record_list[i][7]

            if encoding1:
                self.convert(encoding1)

            if encoding2:
                self.convert(encoding2)

            if encoding3:
                self.convert(encoding3)
    
    def getNameList(self):
        nameList = []

        # MySQL uses CURDATE() to get the current date
        obj = self.run_query(f'''
        SELECT * FROM webapp_attendance
        WHERE DATE(datetime) = CURDATE()
        ''')

        result = obj.fetchall()

        if result:
            for record in result:
                nameid = record[4]
                obj2 = self.run_query(f'''
                                SELECT name FROM webapp_students
                                WHERE id = {nameid}
                                ''')
                
                name = obj2.fetchone()[0]

                nameList.append(name)
            
        return nameList

    def markAttendance(self, name):
        obj = self.run_query(f'''
            SELECT id, grade_id FROM webapp_students
            WHERE name = '{name}'
            ''')

        name_grade = obj.fetchone()

        if name not in self.nameList and name_grade:  # Ensure name_grade is valid
            self.nameList.append(name)
            current = datetime.datetime.now()

            if current.time() > self.late:
                self.run_query(f'''
                    INSERT INTO webapp_attendance (status, datetime, grade_id, name_id)
                    VALUES ('L', '{current}', {name_grade[1]}, {name_grade[0]})
                ''')
            else:
                self.run_query(f'''
                    INSERT INTO webapp_attendance (status, datetime, grade_id, name_id)
                    VALUES ('P', '{current}', {name_grade[1]}, {name_grade[0]})
                ''')
        
        # Use DATE() to extract the date in MySQL
        obj2 = self.run_query(f'''
                        SELECT status, datetime FROM webapp_attendance
                        WHERE DATE(datetime) = CURDATE() AND name_id = {name_grade[0]}
                        ''')

        return obj2.fetchone()
