import sqlite3

DATABASE_NAME = "attendance.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # Registered users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    # Attendance records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, date)
        )
    """)

    connection.commit()
    connection.close()


def add_user(user_id, name, department):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (id, name, department)
            VALUES (?, ?, ?)
            """,
            (user_id, name, department)
        )

        connection.commit()
        print("User saved successfully!")

    except sqlite3.IntegrityError:
        print("Error: This User ID already exists.")

    finally:
        connection.close()


def user_exists(user_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user is not None