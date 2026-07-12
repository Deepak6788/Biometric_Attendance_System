import cv2
import os
import time
import subprocess
import sys
import numpy as np

from database import create_database, add_user, user_exists


# =========================================================
# SETUP
# =========================================================

create_database()

if len(sys.argv) < 4:
    print("Registration details were not provided.")
    sys.exit()

user_id = sys.argv[1]
name = sys.argv[2]
department = sys.argv[3]

if user_exists(user_id):
    print("Error: This User ID is already registered.")
    sys.exit()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FACE_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "faces",
    f"{user_id}_{name}"
)

os.makedirs(FACE_FOLDER, exist_ok=True)


# =========================================================
# FACE DETECTOR
# =========================================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

if face_detector.empty():
    print("Could not load face detector.")
    sys.exit()


# =========================================================
# CAMERA
# =========================================================

camera = cv2.VideoCapture(0)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)

if not camera.isOpened():
    print("Could not open camera.")
    sys.exit()


# =========================================================
# SETTINGS
# =========================================================

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 650

MAX_IMAGES = 20

count = 0

CAPTURE_INTERVAL = 0.7
SHARPNESS_THRESHOLD = 80

last_capture_time = 0

capture_flash_until = 0
capture_message_until = 0


# =========================================================
# POSE INFORMATION
# =========================================================

def get_pose_information(image_count):

    if image_count < 7:

        return (
            "STEP 1 OF 3",
            "LOOK STRAIGHT",
            "Keep your face centered"
        )

    elif image_count < 14:

        return (
            "STEP 2 OF 3",
            "TURN SLIGHTLY LEFT",
            "Move your head slowly"
        )

    else:

        return (
            "STEP 3 OF 3",
            "TURN SLIGHTLY RIGHT",
            "Keep your face visible"
        )


# =========================================================
# DRAW FACE GUIDE
# =========================================================

def draw_face_guide(
    frame,
    center_x,
    center_y,
    radius_x,
    radius_y,
    color
):

    # Main oval
    cv2.ellipse(
        frame,
        (center_x, center_y),
        (radius_x, radius_y),
        0,
        0,
        360,
        color,
        3
    )

    # Decorative guide sections
    cv2.ellipse(
        frame,
        (center_x, center_y),
        (
            radius_x + 8,
            radius_y + 8
        ),
        0,
        210,
        260,
        color,
        6
    )

    cv2.ellipse(
        frame,
        (center_x, center_y),
        (
            radius_x + 8,
            radius_y + 8
        ),
        0,
        280,
        330,
        color,
        6
    )

    cv2.ellipse(
        frame,
        (center_x, center_y),
        (
            radius_x + 8,
            radius_y + 8
        ),
        0,
        30,
        80,
        color,
        6
    )

    cv2.ellipse(
        frame,
        (center_x, center_y),
        (
            radius_x + 8,
            radius_y + 8
        ),
        0,
        100,
        150,
        color,
        6
    )


# =========================================================
# CAMERA WINDOW
# =========================================================

cv2.namedWindow(
    "Biometric Face Registration",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Biometric Face Registration",
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)


# =========================================================
# REGISTRATION LOOP
# =========================================================

while count < MAX_IMAGES:

    success, frame = camera.read()

    if not success:
        print("Could not access camera.")
        break

    # Mirror camera like a selfie camera
    frame = cv2.flip(
        frame,
        1
    )

    frame = cv2.resize(
        frame,
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
    )

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # -----------------------------------------------------
    # FACE GUIDE POSITION
    # -----------------------------------------------------

    center_x = WINDOW_WIDTH // 2
    center_y = 325

    guide_radius_x = 185
    guide_radius_y = 235


    # -----------------------------------------------------
    # SUBTLE BACKGROUND DIMMING
    # -----------------------------------------------------

    dimmed = (
        frame.astype(np.float32)
        * 0.55
    ).astype(np.uint8)

    mask = np.zeros(
        (
            WINDOW_HEIGHT,
            WINDOW_WIDTH
        ),
        dtype=np.uint8
    )

    cv2.ellipse(
        mask,
        (
            center_x,
            center_y
        ),
        (
            guide_radius_x,
            guide_radius_y
        ),
        0,
        0,
        360,
        255,
        -1
    )

    mask_3_channel = cv2.cvtColor(
        mask,
        cv2.COLOR_GRAY2BGR
    )

    frame = np.where(
        mask_3_channel == 255,
        frame,
        dimmed
    )


    # -----------------------------------------------------
    # DETECT FACE
    # -----------------------------------------------------

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(120, 120)
    )


    step_text, pose_text, instruction = (
        get_pose_information(count)
    )


    guide_color = (
        230,
        230,
        230
    )

    status_text = (
        "Position your face inside the guide"
    )

    status_color = (
        255,
        255,
        255
    )


    # -----------------------------------------------------
    # PROCESS DETECTED FACE
    # -----------------------------------------------------

    if len(faces) > 0:

        # Use largest detected face
        x, y, w, h = max(
            faces,
            key=lambda face: (
                face[2]
                * face[3]
            )
        )

        face_center_x = (
            x + w // 2
        )

        face_center_y = (
            y + h // 2
        )


        # Check whether face is near guide center
        horizontal_distance = abs(
            face_center_x
            - center_x
        )

        vertical_distance = abs(
            face_center_y
            - center_y
        )


        if (
            horizontal_distance > 120
            or vertical_distance > 130
        ):

            guide_color = (
                0,
                200,
                255
            )

            status_text = (
                "Move your face to the center"
            )

            status_color = (
                0,
                200,
                255
            )

        else:

            face = gray[
                y:y + h,
                x:x + w
            ]

            sharpness = cv2.Laplacian(
                face,
                cv2.CV_64F
            ).var()


            if (
                sharpness
                < SHARPNESS_THRESHOLD
            ):

                guide_color = (
                    0,
                    165,
                    255
                )

                status_text = (
                    "Hold still - image is blurry"
                )

                status_color = (
                    0,
                    165,
                    255
                )

            else:

                guide_color = (
                    0,
                    255,
                    0
                )

                status_text = (
                    "Perfect - capturing"
                )

                status_color = (
                    0,
                    255,
                    0
                )


                current_time = time.time()


                if (
                    current_time
                    - last_capture_time
                    >= CAPTURE_INTERVAL
                ):

                    face = cv2.resize(
                        face,
                        (
                            200,
                            200
                        )
                    )

                    image_path = os.path.join(
                        FACE_FOLDER,
                        f"image_{count}.jpg"
                    )

                    saved = cv2.imwrite(
                        image_path,
                        face
                    )


                    if saved:

                        count += 1

                        last_capture_time = (
                            current_time
                        )

                        capture_flash_until = (
                            current_time
                            + 0.12
                        )

                        capture_message_until = (
                            current_time
                            + 0.4
                        )

                        print(
                            f"Captured: "
                            f"{count}/"
                            f"{MAX_IMAGES}"
                        )


    # -----------------------------------------------------
    # DRAW FACE GUIDE
    # -----------------------------------------------------

    draw_face_guide(
        frame,
        center_x,
        center_y,
        guide_radius_x,
        guide_radius_y,
        guide_color
    )


    # -----------------------------------------------------
    # TOP INFORMATION
    # -----------------------------------------------------

    cv2.putText(
        frame,
        step_text,
        (
            45,
            55
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (
            220,
            220,
            220
        ),
        2
    )


    cv2.putText(
        frame,
        pose_text,
        (
            45,
            95
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.05,
        (
            255,
            255,
            255
        ),
        2
    )


    cv2.putText(
        frame,
        instruction,
        (
            45,
            128
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (
            210,
            210,
            210
        ),
        1
    )


    # -----------------------------------------------------
    # STATUS MESSAGE
    # -----------------------------------------------------

    cv2.putText(
        frame,
        status_text,
        (
            40,
            555
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        status_color,
        2
    )


    # -----------------------------------------------------
    # CAPTURE CONFIRMATION
    # -----------------------------------------------------

    if (
        time.time()
        < capture_message_until
    ):

        cv2.putText(
            frame,
            "CAPTURED",
            (
                center_x - 85,
                center_y
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (
                0,
                255,
                0
            ),
            3
        )


    # -----------------------------------------------------
    # SUBTLE CAPTURE FLASH
    # -----------------------------------------------------

    if (
        time.time()
        < capture_flash_until
    ):

        flash = np.full_like(
            frame,
            255
        )

        frame = cv2.addWeighted(
            frame,
            0.88,
            flash,
            0.12,
            0
        )


    # -----------------------------------------------------
    # PROGRESS BAR
    # -----------------------------------------------------

    progress_x = 40
    progress_y = 590

    progress_width = 850
    progress_height = 10


    # Background
    cv2.rectangle(
        frame,
        (
            progress_x,
            progress_y
        ),
        (
            progress_x
            + progress_width,
            progress_y
            + progress_height
        ),
        (
            80,
            80,
            80
        ),
        -1
    )


    completed_width = int(
        (
            count
            / MAX_IMAGES
        )
        * progress_width
    )


    cv2.rectangle(
        frame,
        (
            progress_x,
            progress_y
        ),
        (
            progress_x
            + completed_width,
            progress_y
            + progress_height
        ),
        (
            0,
            255,
            0
        ),
        -1
    )


    # Progress number
    cv2.putText(
        frame,
        f"{count} / {MAX_IMAGES}",
        (
            920,
            602
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (
            255,
            255,
            255
        ),
        2
    )


    # Cancel instruction
    cv2.putText(
        frame,
        "Press Q to cancel",
        (
            465,
            635
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (
            200,
            200,
            200
        ),
        1
    )


    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    cv2.imshow(
        "Biometric Face Registration",
        frame
    )


    if (
        cv2.waitKey(1)
        & 0xFF
        == ord("q")
    ):
        break


# =========================================================
# CLOSE CAMERA
# =========================================================

camera.release()

cv2.destroyAllWindows()


# =========================================================
# COMPLETE REGISTRATION
# =========================================================

if count == MAX_IMAGES:

    add_user(
        user_id,
        name,
        department
    )

    print(
        "Registration completed successfully!"
    )

    print(
        "Training face recognition model..."
    )

    train_file = os.path.join(
        BASE_DIR,
        "train.py"
    )

    subprocess.run([
        sys.executable,
        train_file
    ])

    print(
        "New user is ready for attendance."
    )

else:

    print(
        "Registration was cancelled "
        "or not completed."
    )