import sqlite3
from datetime import datetime

class AttendanceSystem:
    def __init__(self, db_name="university_system.db"):
        # الاتصال بقاعدة البيانات (سيتم إنشاء الملف تلقائياً إذا لم يكن موجوداً)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """إنشاء الجداول اللازمة بنظام العلاقات (Relational Schema)"""
        
        # 1. جدول الطلاب
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT
            )
        ''')

        # 2. جدول المحاضرات (يخزن الموضوع والتاريخ)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lectures (
                lecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                timestamp TEXT
            )
        ''')

        # 3. جدول الحضور (يربط الطالب بالمحاضرة مع وقت التسجيل)
        # هذا الجدول يمثل علاقة Many-to-Many
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                lecture_id INTEGER,
                marked_at TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id),
                FOREIGN KEY(lecture_id) REFERENCES lectures(lecture_id),
                UNIQUE(student_id, lecture_id) -- منع تكرار الحضور لنفس المحاضرة
            )
        ''')
        self.conn.commit()

    def add_student(self, student_id, name):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO students (student_id, name, created_at) VALUES (?, ?, ?)", 
                                (student_id, name, timestamp))
            self.conn.commit()
            print(f"✅ Success: Student {name} added to Database.")
        except sqlite3.IntegrityError:
            print(f"❌ Error: Student ID {student_id} already exists!")

    def start_new_lecture(self, topic="General Lecture"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO lectures (topic, timestamp) VALUES (?, ?)", (topic, timestamp))
        self.conn.commit()
        
        # الحصول على ID المحاضرة التي تم إنشاؤها للتو
        lecture_id = self.cursor.lastrowid
        print(f"\n📘 New Lecture Started (ID: {lecture_id}) - Topic: {topic}")
        return lecture_id

    def get_current_lecture_id(self):
        """جلب آخر محاضرة تم إنشاؤها"""
        self.cursor.execute("SELECT lecture_id FROM lectures ORDER BY lecture_id DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0] if result else None

    def record_attendance(self, student_id):
        lecture_id = self.get_current_lecture_id()
        
        if not lecture_id:
            print("❌ Error: No lectures started yet.")
            return

        # التحقق من وجود الطالب أولاً
        self.cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
        student = self.cursor.fetchone()
        
        if not student:
            print("❌ Error: Student ID not found in database.")
            return

        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO attendance (student_id, lecture_id, marked_at) VALUES (?, ?, ?)", 
                                (student_id, lecture_id, current_time))
            self.conn.commit()
            print(f"✅ Attendance marked for {student[0]} at {current_time}")
        
        except sqlite3.IntegrityError:
            print(f"⚠️ Warning: {student[0]} is already marked present for this lecture.")

    def generate_report(self):
        print("\n" + "="*40)
        print("📊 PROFESSIONAL ATTENDANCE ANALYTICS")
        print("="*40)

        # 1. حساب إجمالي المحاضرات
        self.cursor.execute("SELECT COUNT(*) FROM lectures")
        total_lectures = self.cursor.fetchone()[0]

        if total_lectures == 0:
            print("No lectures recorded yet.")
            return

        print(f"Total Lectures Conducted: {total_lectures}\n")
        print(f"{'Name':<20} | {'Attended':<10} | {'Rate':<10} | {'Status'}")
        print("-" * 60)

        # 2. استعلام معقد (Aggregation) لجمع البيانات
        # هذا الاستعلام يجلب كل الطلاب ويحسب عدد مرات حضورهم
        query = '''
            SELECT s.name, COUNT(a.lecture_id) as attendance_count
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id
        '''
        
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        for name, count in records:
            percentage = (count / total_lectures) * 100
            status = "✅ Good" if percentage >= 75 else "⚠️ Low Attendance"
            if percentage < 50: status = "🚨 CRITICAL"
            
            print(f"{name:<20} | {count}/{total_lectures:<8} | {percentage:.1f}%     | {status}")
        
        print("-" * 60 + "\n")

    def close(self):
        self.conn.close()

# =========================
# Main Execution
# =========================
if __name__ == "__main__":
    system = AttendanceSystem()

    while True:
        print("\n1. Add Student")
        print("2. Start New Lecture")
        print("3. Mark Attendance")
        print("4. Analytics Report")
        print("5. Exit")
        
        choice = input("Select Option: ")

        if choice == '1':
            uid = input("Enter ID: ")
            name = input("Enter Name: ")
            system.add_student(uid, name)
        
        elif choice == '2':
            topic = input("Enter Lecture Topic (e.g., Physics, Calculus): ")
            system.start_new_lecture(topic)

        elif choice == '3':
            uid = input("Scan Student ID: ")
            system.record_attendance(uid)

        elif choice == '4':
            system.generate_report()

        elif choice == '5':
            system.close()
            print("System Shutdown.")
            break