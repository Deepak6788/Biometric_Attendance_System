import csv
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(BASE_DIR, "attendance.db")

export_folder = os.path.join(BASE_DIR, "attendance")
os.makedirs(export_folder, exist_ok=True)

connection = sqlite3.connect(database_path)
cursor = connection.cursor()

cursor.execute("""
    SELECT
        users.id,
        users.name,
        users.department,
        attendance.date,
        attendance.time
    FROM attendance
    JOIN users
    ON attendance.user_id = users.id
    ORDER BY attendance.date, attendance.time
""")

records = cursor.fetchall()
connection.close()

if not records:
    print("No attendance records available to export.")

else:
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    file_path = os.path.join(
        export_folder,
        f"attendance_{current_time}.csv"
    )

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "User ID",
            "Name",
            "Department",
            "Date",
            "Time"
        ])

        writer.writerows(records)

    print("Attendance exported successfully!")
    print(f"Saved to: {file_path}")