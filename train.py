import cv2
import os
import numpy as np

faces_folder = "data/faces"
trainer_folder = "trainer"

os.makedirs(trainer_folder, exist_ok=True)

# Create LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

face_images = []
face_ids = []

# Read each registered user's folder
for folder_name in os.listdir(faces_folder):

    folder_path = os.path.join(faces_folder, folder_name)

    if not os.path.isdir(folder_path):
        continue

    # Folder format: ID_Name
    try:
        user_id = int(folder_name.split("_")[0])
    except ValueError:
        print(f"Skipping invalid folder: {folder_name}")
        continue

    # Read all face images
    for image_name in os.listdir(folder_path):

        image_path = os.path.join(
            folder_path,
            image_name
        )

        image = cv2.imread(
            image_path,
            cv2.IMREAD_GRAYSCALE
        )

        if image is not None:
            face_images.append(image)
            face_ids.append(user_id)

# Make sure training data exists
if len(face_images) == 0:
    print("No face images found. Register a user first.")

else:
    # Train the model
    recognizer.train(
        face_images,
        np.array(face_ids)
    )

    # Save trained model
    model_path = "trainer/trainer.yml"
    recognizer.write(model_path)

    print("Face recognition model trained successfully!")
    print(f"Total images used: {len(face_images)}")
    print(f"Model saved to: {model_path}")