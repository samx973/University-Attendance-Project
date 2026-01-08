import sqlite3
from datetime import datetime

class UniAttendance:
    def __init__(self):
        self.db_name = "attendance.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Create tables
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT,
                reg_date TEXT
            )
        ''')
        
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                date_time TEXT
            )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                std_id TEXT,
                lec_id INTEGER,
                time_in TEXT,
                FOREIGN KEY(std_id) REFERENCES students(id),
                FOREIGN KEY(lec_id) REFERENCES lectures(id)
            )
        ''')
        self.conn.commit()

    def add_student(self, sid, name):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.c.execute("INSERT INTO students VALUES (?, ?, ?)", (sid, name, now))
            self.conn.commit()
            print("Student added.")
        except:
            print("Error: Student ID might already exist.")

    def new_lecture(self, sub):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("INSERT INTO lectures (subject, date_time) VALUES (?, ?)", (sub, now))
        self.conn.commit()
        print(f"Lecture '{sub}' started.")

    def mark_present(self, sid):
        # Get last lecture ID
        self.c.execute("SELECT id FROM lectures ORDER BY id DESC LIMIT 1")
        last_lec = self.c.fetchone()
        
        if not last_lec:
            print("No active lecture found.")
            return

        lec_id = last_lec[0]
        now = datetime.now().strftime("%H:%M:%S")
        
        # Check if student exists
        self.c.execute("SELECT name FROM students WHERE id=?", (sid,))
        res = self.c.fetchone()
        
        if res:
            try:
                # Prevent duplicate attendance for same lecture
                self.c.execute("SELECT * FROM records WHERE std_id=? AND lec_id=?", (sid, lec_id))
                if self.c.fetchone():
                    print("Already registered.")
                else:
                    self.c.execute("INSERT INTO records (std_id, lec_id, time_in) VALUES (?, ?, ?)", 
                                 (sid, lec_id, now))
                    self.conn.commit()
                    print(f"Marked: {res[0]}")
            except Exception as e:
                print(e)
        else:
            print("Student not found.")

    def show_stats(self):
        print("\n--- Attendance Report ---")
        
        self.c.execute("SELECT COUNT(*) FROM lectures")
        total_lecs = self.c.fetchone()[0]
        
        if total_lecs == 0:
            print("No lectures yet.")
            return

        # Get all students and their count
        query = '''
            SELECT s.name, COUNT(r.lec_id) 
            FROM students s 
            LEFT JOIN records r ON s.id = r.std_id 
            GROUP BY s.id
        '''
        self.c.execute(query)
        data = self.c.fetchall()
        
        for name, count in data:
            perc = (count / total_lecs) * 100
            print(f"{name}: {count}/{total_lecs} ({int(perc)}%)")

    def close(self):
        self.conn.close()

# Main loop
if __name__ == "__main__":
    sys = UniAttendance()
    
    while True:
        print("\n1. New Student")
        print("2. Start Lecture")
        print("3. Take Attendance")
        print("4. Stats")
        print("5. Exit")
        
        ch = input(">> ")
        
        if ch == '1':
            i = input("ID: ")
            n = input("Name: ")
            sys.add_student(i, n)
        elif ch == '2':
            s = input("Subject: ")
            sys.new_lecture(s)
        elif ch == '3':
            i = input("Student ID: ")
            sys.mark_present(i)
        elif ch == '4':
            sys.show_stats()
        elif ch == '5':
            sys.close()
            break
        ##test
        