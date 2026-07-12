import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import sqlite3
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "attendance.db")


# Run another Python file
def run_file(filename):
    try:
        subprocess.Popen([
            sys.executable,
            os.path.join(BASE_DIR, filename)
        ])

    except Exception as error:
        messagebox.showerror(
            "Error",
            str(error)
        )


# Get dashboard statistics
def get_dashboard_counts():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        # Count registered users
        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        users_count = cursor.fetchone()[0]

        # Count today's attendance
        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            """,
            (today,)
        )

        attendance_count = cursor.fetchone()[0]

        connection.close()

        users_value.config(
            text=str(users_count)
        )

        attendance_value.config(
            text=str(attendance_count)
        )

    except sqlite3.Error:

        users_value.config(text="0")
        attendance_value.config(text="0")


# Update live date and time
def update_clock():
    current = datetime.now()

    clock_label.config(
        text=current.strftime(
            "%A, %d %B %Y  |  %I:%M:%S %p"
        )
    )

    # Update every second
    root.after(
        1000,
        update_clock
    )


# Registration window
def open_registration():

    registration_window = tk.Toplevel(root)

    registration_window.title(
        "Register New User"
    )

    registration_window.geometry(
        "450x400"
    )

    registration_window.resizable(
        False,
        False
    )

    # Heading
    tk.Label(
        registration_window,
        text="Register New User",
        font=("Arial", 20, "bold")
    ).pack(
        pady=25
    )

    # Form
    form = tk.Frame(
        registration_window
    )

    form.pack(
        pady=10
    )

    # User ID
    tk.Label(
        form,
        text="User ID:",
        font=("Arial", 12)
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    id_entry = tk.Entry(
        form,
        width=25,
        font=("Arial", 12)
    )

    id_entry.grid(
        row=0,
        column=1
    )

    # Name
    tk.Label(
        form,
        text="Name:",
        font=("Arial", 12)
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    name_entry = tk.Entry(
        form,
        width=25,
        font=("Arial", 12)
    )

    name_entry.grid(
        row=1,
        column=1
    )

    # Department
    tk.Label(
        form,
        text="Department:",
        font=("Arial", 12)
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    department_entry = tk.Entry(
        form,
        width=25,
        font=("Arial", 12)
    )

    department_entry.grid(
        row=2,
        column=1
    )

    # Start registration
    def start_registration():

        user_id = (
            id_entry.get().strip()
        )

        name = (
            name_entry.get().strip()
        )

        department = (
            department_entry
            .get()
            .strip()
        )

        # Check empty fields
        if (
            not user_id
            or not name
            or not department
        ):

            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )

            return

        try:

            subprocess.Popen([
                sys.executable,
                os.path.join(
                    BASE_DIR,
                    "register.py"
                ),
                user_id,
                name,
                department
            ])

            registration_window.destroy()

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    # Registration button
    tk.Button(
        registration_window,
        text="Start Face Registration",
        width=25,
        height=2,
        command=start_registration
    ).pack(
        pady=25
    )


# -------------------------
# Main Application Window
# -------------------------

root = tk.Tk()

root.title(
    "Biometric Attendance System"
)

root.geometry(
    "750x700"
)

root.resizable(
    False,
    False
)


# Main heading
tk.Label(
    root,
    text="Biometric Attendance System",
    font=("Arial", 26, "bold")
).pack(
    pady=(30, 5)
)


# Subtitle
tk.Label(
    root,
    text="Face Recognition Attendance Dashboard",
    font=("Arial", 12)
).pack(
    pady=(0, 10)
)


# Live clock
clock_label = tk.Label(
    root,
    text="",
    font=("Arial", 11, "bold")
)

clock_label.pack(
    pady=(0, 15)
)


# Dashboard statistics
stats_frame = tk.Frame(root)

stats_frame.pack(
    pady=10
)


# Registered Users card
users_card = tk.LabelFrame(
    stats_frame,
    text="Registered Users",
    width=250,
    height=100
)

users_card.grid(
    row=0,
    column=0,
    padx=15
)

users_card.pack_propagate(
    False
)


users_value = tk.Label(
    users_card,
    text="0",
    font=("Arial", 28, "bold")
)

users_value.pack(
    expand=True
)


# Attendance Today card
attendance_card = tk.LabelFrame(
    stats_frame,
    text="Attendance Today",
    width=250,
    height=100
)

attendance_card.grid(
    row=0,
    column=1,
    padx=15
)

attendance_card.pack_propagate(
    False
)


attendance_value = tk.Label(
    attendance_card,
    text="0",
    font=("Arial", 28, "bold")
)

attendance_value.pack(
    expand=True
)


# Action buttons
button_frame = tk.Frame(root)

button_frame.pack(
    pady=25
)


buttons = [

    (
        "Register New User",
        open_registration
    ),

    (
        "View Registered Users",
        lambda: run_file(
            "view_users.py"
        )
    ),

    (
        "Start Attendance",
        lambda: run_file(
            "attendance.py"
        )
    ),

    (
        "View Attendance Records",
        lambda: run_file(
            "view_attendance.py"
        )
    ),

    (
        "Export Attendance to CSV",
        lambda: run_file(
            "export_attendance.py"
        )
    ),

    (
        "Train Face Recognition Model",
        lambda: run_file(
            "train.py"
        )
    )
]


# Create buttons in two columns
for index, (
    text,
    command
) in enumerate(buttons):

    row = index // 2
    column = index % 2

    tk.Button(
        button_frame,
        text=text,
        width=28,
        height=2,
        font=("Arial", 11),
        command=command
    ).grid(
        row=row,
        column=column,
        padx=10,
        pady=10
    )


# Refresh dashboard
tk.Button(
    root,
    text="Refresh Dashboard",
    width=25,
    height=2,
    command=get_dashboard_counts
).pack(
    pady=5
)


# Exit button
tk.Button(
    root,
    text="Exit",
    width=25,
    height=2,
    command=root.destroy
).pack(
    pady=8
)


# Load dashboard information
get_dashboard_counts()

# Start live clock
update_clock()

# Start application
root.mainloop()