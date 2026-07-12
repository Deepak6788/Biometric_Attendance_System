from datetime import datetime
import cv2
import os
import sqlite3

from database import create_database

create_database()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "trainer",
    "trainer.yml"
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "attendance.db"
)

# Check trained model
if not os.path.exists(MODEL_PATH):
    print("Trained model not found. Register a user first.")
    raise SystemExit

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

# Load face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

# Database connection
connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

# Recognition confirmation settings
required_frames = 10
last_user_id = None
recognition_count = 0
confirmed_users = set()

# Open camera
camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        print("Could not access camera.")
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:

        face = gray[y:y + h, x:x + w]

        face = cv2.resize(
            face,
            (200, 200)
        )

        user_id, confidence = recognizer.predict(face)

        # Lower LBPH value means a better match
        if confidence < 70:

            cursor.execute(
                """
                SELECT name, department
                FROM users
                WHERE id = ?
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if user:

                name = user[0]
                department = user[1]

                # Count consecutive recognitions
                if user_id == last_user_id:
                    recognition_count += 1
                else:
                    last_user_id = user_id
                    recognition_count = 1

                # Waiting for confirmation
                if recognition_count < required_frames:

                    label = (
                        f"Verifying {name} "
                        f"{recognition_count}/{required_frames}"
                    )

                    box_color = (0, 255, 255)

                else:

                    label = f"{name} - Attendance Marked"
                    box_color = (0, 255, 0)

                    # Mark only once during this session
                    if user_id not in confirmed_users:

                        current_time = datetime.now()

                        date = current_time.strftime(
                            "%Y-%m-%d"
                        )

                        time = current_time.strftime(
                            "%H:%M:%S"
                        )

                        try:

                            cursor.execute(
                                """
                                INSERT INTO attendance
                                (user_id, date, time)
                                VALUES (?, ?, ?)
                                """,
                                (user_id, date, time)
                            )

                            connection.commit()

                            print(
                                f"Attendance marked: "
                                f"{name} | {date} | {time}"
                            )

                        except sqlite3.IntegrityError:

                            print(
                                f"{name}'s attendance "
                                f"is already marked today."
                            )

                        confirmed_users.add(user_id)

            else:

                label = "Unknown"
                box_color = (0, 0, 255)

                last_user_id = None
                recognition_count = 0

        else:

            label = "Unknown"
            box_color = (0, 0, 255)

            last_user_id = None
            recognition_count = 0

        # Draw face box
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            box_color,
            2
        )

        # Display recognition status
        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            box_color,
            2
        )

    cv2.imshow(
        "Biometric Attendance - Press Q to Quit",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
connection.close()
cv2.destroyAllWindows()