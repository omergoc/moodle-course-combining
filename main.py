import requests
import json
import random
import time

class Main:

    def __init__(self):
        self.url = 'MOODLE URL'
        self.token = "TOKEN"
        self.numsection = '16'
        self.categoryid = 84
        self.startdate = '2022-09-19 00:00:00'

    def start_app(self):
        print('-'*56)
        print('-'*56)
        print(f"{'-'*10} MOODLE DERS BİRLEŞTİRME OTOMASYONU {'-'*10}")
        print('-'*56)
        print('-'*56)
        print()

    def create_courses(self):
        __fullname = input("Ortak Ders Adı: ")
        __shortname = input("Ortak Ders Kısa Adı: ")
        timestamp = int(time.mktime(time.strptime(self.startdate, '%Y-%m-%d %H:%M:%S')))
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses[0][fullname]': __fullname,
            'courses[0][shortname]': __shortname,
            'courses[0][idnumber]': str(random.randint(1000000,2000000)),
            'courses[0][categoryid]': self.categoryid,
            'courses[0][numsections]': self.numsection,
            'courses[0][startdate]': timestamp
        }
        try:
            response = self.post_curl(self.url, params)
        except:
            response = "Hatalı createCourses Fonksiyonu"

        return response

    def post_curl(self, url, params):
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        req = requests.post(url, headers=headers, data=params)
        result = req.json()
        return result

    def json_get(self,json_name):
        file = open(f"jsons/{json_name}.json")
        json_data = json.load(file)
        file.close()
        return json_data

    def json_create(self,json_list,json_name):
        with open(f'jsons/{json_name}.json', 'w', encoding="utf-8") as file:
            json.dump(json_list, file)

    def user_get_course_list(self):
        data_courses = app.json_get('course')
        limit_course = int(input("Kaç Adet Kurs Birleştirmek İsitiyorsunuz ? :"))
        join_list = []
        i = 0
        for item in range(0, limit_course):
            id_number = input("Dersin Haraket ID sini Giriniz ? : ")
            for item2 in data_courses:
                parse_id = item2['idnumber'].split('-')
                if len(parse_id) > 2:
                    if id_number in parse_id[4]:
                        join_list.append(item2)
        return join_list

    def get_users_list(self,data):
        arr = []
        for course in data:
            params = {
                'wstoken': self.token,
                'wsfunction': 'core_enrol_get_enrolled_users',
                'moodlewsrestformat': 'json',
                'courseid' : course['id']
            }
            try:
                get_json = self.post_curl(self.url, params)
                for item in get_json:
                    json_data = {
                        'userid':item['id'],
                        'role':item['roles'],
                        'courseid':course['id']
                    }
                    arr.append(json_data)
            except:
                print("Hatalı get_users_list Fonksiyonu")

        return arr

    def enrol_course(self,common_course,data):
        for user in data:
            params = {
                'wstoken': self.token,
                'wsfunction': 'enrol_manual_enrol_users',
                'moodlewsrestformat': 'json',
                'enrolments[0][roleid]': int(user['role'][0]['roleid']),
                'enrolments[0][userid]': int(user['userid']),
                'enrolments[0][courseid]': int(common_course),
            }
            try:
                response = self.post_curl(self.url, params)
            except:
                print("Hatalı enrolCourse Fonksiyonu")

        return response

    def get_courses(self):
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json'
        }
        arr = []
        try:
            get_json = self.post_curl(self.url, params)
            for item in get_json:
                if item['idnumber'] not in '':
                    json = {
                        'id': item['id'],
                        'categoryid': item['categoryid'],
                        'shortname':item['shortname'],
                        'idnumber':item['idnumber'],
                    }
                    arr.append(json)
        except:
            print("Hatalı get_courses Fonksiyonu")

        return arr

    def report_data_create(self):
        arr_report = []
        join_arr = self.json_get("join-list")
        user_arr = self.json_get("users")
        for course in join_arr:
            user_count = 0
            for user in  user_arr:
                if course['id'] == user['courseid']:
                    user_count+=1

            json_data = {
                'course_shortname': course['shortname'],
                'course_user_count': user_count
            }
            arr_report.append(json_data)

        return arr_report

    def report_log_read(self,report_list):
        print('-'*43)
        print(f"{'-'*10} BİRLEŞTİRİLEN DERSLER {'-'*10}")
        print('-'*43)
        for report in report_list:
            print(f"Dersin Adı: {report['course_shortname']}")
            print(f"Dersin Toplam Öğrenci Sayısı: {report['course_user_count']}")
            print('-'*10)
            
        print('-'*43)

if __name__ == '__main__':  
    app = Main()
    app.start_app()
    control_file = input("Kurs Listesi Güncellensin Mi ? (E/H): ").lower()

    if control_file == 'e':
        print("Güncel Kurs Verileri İndiriliyor...")
        courses_list = app.get_courses()
        app.json_create(courses_list, "course")
        print("Kurs Listesi Güncellendi...")
        print("-")

    join_list = app.user_get_course_list()
    print("Birleştirilecek Kurs Datası Oluşturuldu...")
    print("-")
    app.json_create(join_list, "join-list")
    create_course = app.create_courses()
    print("Ortak Ders Oluşuturuldu...")
    print("-")
    common_course = create_course[0]['id']

    users_list = app.get_users_list(app.json_get("join-list"))
    print("Kullanıcı Datası Oluşturuldu...")

    app.json_create(users_list, "users")
    print("-")
    print("Kullanıcı Ekleme İşlemi Devam ediyor...")
    app.enrol_course(common_course,app.json_get("users"))
    print("-")
    print("Ortak Derse Kullanıcılar Eklendi.")
    print("-")
    report_list = app.report_data_create()
    print("Rapor JSON Oluşturuldu...")

    app.json_create(report_list, "report")

    app.report_log_read(app.json_get("report"))
