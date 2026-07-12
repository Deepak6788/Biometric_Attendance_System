import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "attendance.db")
FACES_FOLDER = os.path.join(BASE_DIR, "data", "faces")


def load_users():
    # Clear existing rows
    for item in table.get_children():
        table.delete(item)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, department
        FROM users
        ORDER BY id
    """)

    users = cursor.fetchall()
    connection.close()

    for user in users:
        table.insert(
            "",
            "end",
            values=user
        )


def delete_user():
    selected_item = table.selection()

    if not selected_item:
        messagebox.showwarning(
            "No User Selected",
            "Please select a user to delete."
        )
        return

    user_data = table.item(
        selected_item[0],
        "values"
    )

    user_id = user_data[0]
    name = user_data[1]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete {name} and all related data?"
    )

    if not confirm:
        return

    # Delete attendance and user from database
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM attendance WHERE user_id = ?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()

    # Delete user's face images
    user_folder = os.path.join(
        FACES_FOLDER,
        f"{user_id}_{name}"
    )

    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)

    # Retrain model
    subprocess.run([
        sys.executable,
        os.path.join(BASE_DIR, "train.py")
    ])

    messagebox.showinfo(
        "Success",
        f"{name} was deleted successfully."
    )

    load_users()


# Window
window = tk.Tk()
window.title("Registered Users")
window.geometry("700x500")

tk.Label(
    window,
    text="Registered Users",
    font=("Arial", 20, "bold")
).pack(pady=20)

columns = (
    "ID",
    "Name",
    "Department"
)

table = ttk.Treeview(
    window,
    columns=columns,
    show="headings"
)

for column in columns:
    table.heading(column, text=column)
    table.column(
        column,
        anchor="center"
    )

table.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

tk.Button(
    window,
    text="Delete Selected User",
    command=delete_user,
    width=25,
    height=2
).pack(pady=15)

load_users()

window.mainloop()