import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "attendance.db")


def load_records():
    # Clear existing rows
    for item in table.get_children():
        table.delete(item)

    search_text = search_entry.get().strip()
    date_text = date_entry.get().strip()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        SELECT
            users.id,
            users.name,
            users.department,
            attendance.date,
            attendance.time
        FROM attendance
        JOIN users
        ON attendance.user_id = users.id
        WHERE 1 = 1
    """

    parameters = []

    # Search by ID or name
    if search_text:
        query += """
            AND (
                CAST(users.id AS TEXT) LIKE ?
                OR users.name LIKE ?
            )
        """

        search_value = f"%{search_text}%"
        parameters.extend([
            search_value,
            search_value
        ])

    # Filter by exact date
    if date_text:
        query += " AND attendance.date = ?"
        parameters.append(date_text)

    query += """
        ORDER BY attendance.date DESC,
                 attendance.time DESC
    """

    cursor.execute(
        query,
        parameters
    )

    records = cursor.fetchall()
    connection.close()

    # Add records to table
    for record in records:
        table.insert(
            "",
            "end",
            values=record
        )

    total_label.config(
        text=f"Total Records: {len(records)}"
    )


def clear_filters():
    search_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    load_records()


# Main window
window = tk.Tk()

window.title("Attendance Records")
window.geometry("900x550")

# Heading
tk.Label(
    window,
    text="Attendance Records",
    font=("Arial", 22, "bold")
).pack(pady=20)


# Search and filter section
filter_frame = tk.Frame(window)
filter_frame.pack(pady=10)


tk.Label(
    filter_frame,
    text="Search ID / Name:"
).grid(
    row=0,
    column=0,
    padx=5
)

search_entry = tk.Entry(
    filter_frame,
    width=20
)

search_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    filter_frame,
    text="Date (YYYY-MM-DD):"
).grid(
    row=0,
    column=2,
    padx=5
)

date_entry = tk.Entry(
    filter_frame,
    width=15
)

date_entry.grid(
    row=0,
    column=3,
    padx=5
)


tk.Button(
    filter_frame,
    text="Search",
    command=load_records
).grid(
    row=0,
    column=4,
    padx=5
)


tk.Button(
    filter_frame,
    text="Clear",
    command=clear_filters
).grid(
    row=0,
    column=5,
    padx=5
)


# Table frame
table_frame = tk.Frame(window)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)


columns = (
    "ID",
    "Name",
    "Department",
    "Date",
    "Time"
)


table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


for column in columns:

    table.heading(
        column,
        text=column
    )

    table.column(
        column,
        anchor="center",
        width=150
    )


# Scrollbar
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

table.configure(
    yscrollcommand=scrollbar.set
)


table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# Bottom section
bottom_frame = tk.Frame(window)

bottom_frame.pack(
    fill="x",
    padx=20,
    pady=10
)


total_label = tk.Label(
    bottom_frame,
    text="Total Records: 0",
    font=("Arial", 11, "bold")
)

total_label.pack(
    side="left"
)


tk.Button(
    bottom_frame,
    text="Refresh",
    width=15,
    command=load_records
).pack(
    side="right"
)


# Load records when window opens
load_records()

window.mainloop()