# # # # # # import streamlit as st
# # # # # # import mysql.connector
# # # # # # import requests
# # # # # # import face_recognition
# # # # # # import os
# # # # # # import pyttsx3
# # # # # # import threading
# # # # # # import cv2
# # # # # # import numpy as np
# # # # # # from PIL import Image
# # # # # # import io

# # # # # # # ESP32-CAM IP address
# # # # # # ESP32CAM_IP = "http://192.168.147.81/capture"
# # # # # # SAVE_PATH = "captured_image.jpg"

# # # # # # # Function to connect to the MySQL database
# # # # # # def connect_db():
# # # # # #     return mysql.connector.connect(
# # # # # #         host="localhost",
# # # # # #         user="root",
# # # # # #         password="Indira@1943",
# # # # # #         database="second_eye"
# # # # # #     )

# # # # # # # Function to announce audio message in a separate thread
# # # # # # def announce(message):
# # # # # #     def speak():
# # # # # #         engine = pyttsx3.init()
# # # # # #         engine.say(message)
# # # # # #         engine.runAndWait()
    
# # # # # #     thread = threading.Thread(target=speak)
# # # # # #     thread.start()

# # # # # # # Function to detect faces using OpenCV
# # # # # # def detect_faces_opencv(image):
# # # # # #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
# # # # # #     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# # # # # #     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
# # # # # #     return faces  # Returns a list of bounding boxes (x, y, w, h)

# # # # # # # Function to encode faces using face_recognition
# # # # # # def encode_faces(image):
# # # # # #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # # # # #     face_locations = face_recognition.face_locations(rgb_image)
# # # # # #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
# # # # # #     return face_encodings, face_locations  # Return encodings + bounding box locations

# # # # # # # Function to recognize faces and return individual matches
# # # # # # def recognize_faces(captured_encodings):
# # # # # #     conn = connect_db()
# # # # # #     cursor = conn.cursor()
# # # # # #     cursor.execute("SELECT image_name, image_data FROM images")
# # # # # #     data = cursor.fetchall()
# # # # # #     cursor.close()
# # # # # #     conn.close()

# # # # # #     face_results = []  # Store per-face results

# # # # # #     for idx, captured_encoding in enumerate(captured_encodings):
# # # # # #         best_match = "Unknown"  # Default if no match is found
# # # # # #         min_distance = 0.6  # Threshold for accuracy

# # # # # #         for image_name, image_blob in data:
# # # # # #             stored_image = np.array(Image.open(io.BytesIO(image_blob)))
# # # # # #             stored_encodings, _ = encode_faces(stored_image)

# # # # # #             for stored_encoding in stored_encodings:
# # # # # #                 distance = face_recognition.face_distance([stored_encoding], captured_encoding)[0]
# # # # # #                 if distance < min_distance:  # Choose the best match with lowest distance
# # # # # #                     min_distance = distance
# # # # # #                     best_match = image_name  # Update best match
        
# # # # # #         face_results.append(best_match)  # Store only the best match per face

# # # # # #     return face_results

# # # # # # # Function to draw bounding boxes and labels on image
# # # # # # def draw_bounding_boxes(image, face_locations, match_results):
# # # # # #     for (top, right, bottom, left), name in zip(face_locations, match_results):
# # # # # #         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)  # Green box
# # # # # #         cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# # # # # #     return image

# # # # # # # Function to upload image to the database
# # # # # # def upload_image_to_db(image, image_name):
# # # # # #     conn = connect_db()
# # # # # #     cursor = conn.cursor()
# # # # # #     image_bytes = io.BytesIO()
# # # # # #     image.save(image_bytes, format='JPEG')
# # # # # #     image_data = image_bytes.getvalue()
    
# # # # # #     cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)",
# # # # # #                    (image_name, image_data))
# # # # # #     conn.commit()
# # # # # #     cursor.close()
# # # # # #     conn.close()

# # # # # # # Function to retrieve images from the database
# # # # # # def retrieve_images():
# # # # # #     conn = connect_db()
# # # # # #     cursor = conn.cursor()
# # # # # #     cursor.execute("SELECT image_name, image_data FROM images")
# # # # # #     data = cursor.fetchall()
# # # # # #     cursor.close()
# # # # # #     conn.close()
# # # # # #     return data

# # # # # # # Streamlit UI
# # # # # # st.title("Second Eye - Image Recognition System 👁️👁️")

# # # # # # # Sidebar navigation
# # # # # # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # # # # # if page == "Home":
# # # # # #     st.subheader("Welcome to the Home Page")

# # # # # #     response = requests.get(ESP32CAM_IP)
# # # # # #     if response.status_code == 200:
# # # # # #         with open(SAVE_PATH, "wb") as file:
# # # # # #             file.write(response.content)

# # # # # #         captured_image = cv2.imread(SAVE_PATH)
# # # # # #         captured_encodings, face_locations = encode_faces(captured_image)

# # # # # #         if captured_encodings:
# # # # # #             match_results = recognize_faces(captured_encodings)

# # # # # #             # Draw bounding boxes with names
# # # # # #             processed_image = draw_bounding_boxes(captured_image, face_locations, match_results)

# # # # # #             # Convert to PIL Image for Streamlit
# # # # # #             processed_pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
# # # # # #             st.image(processed_pil_image, caption="Processed Image with Matches", use_column_width=True)

# # # # # #             if len(match_results) == 1:
# # # # # #                 name = match_results[0]
# # # # # #                 announce(f"Single face detected: Match found with {name}")
# # # # # #                 st.success(f"Single face detected: Match found with {name}")
# # # # # #             else:
# # # # # #                 for idx, name in enumerate(match_results, 1):
# # # # # #                     announce(f"Face {idx}: Match found with {name}")
# # # # # #                     st.success(f"Face {idx}: Match found with {name}")

# # # # # #         else:
# # # # # #             announce("No face detected in captured image")
# # # # # #             st.error("No face detected in captured image")

# # # # # #         os.remove(SAVE_PATH)
# # # # # #     else:
# # # # # #         st.error("Failed to capture image")
# # # # # #         announce("Failed to capture image")

# # # # # # elif page == "Supervisor":
# # # # # #     st.subheader("Upload Image")
# # # # # #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# # # # # #     image_name = st.text_input("Enter Image Name")

# # # # # #     if st.button("Upload") and uploaded_image and image_name:
# # # # # #         image = Image.open(uploaded_image)
# # # # # #         upload_image_to_db(image, image_name)
# # # # # #         st.success("Image uploaded successfully!")

# # # # # # elif page == "User":
# # # # # #     st.subheader("Retrieve Images")
# # # # # #     images_data = retrieve_images()

# # # # # #     for image_name, image_blob in images_data:
# # # # # #         image = Image.open(io.BytesIO(image_blob))
# # # # # #         st.image(image, caption=image_name, use_column_width=True)


# # # # # import streamlit as st
# # # # # import mysql.connector
# # # # # import requests
# # # # # import face_recognition
# # # # # import os
# # # # # import pyttsx3
# # # # # import threading
# # # # # import cv2
# # # # # import numpy as np
# # # # # from PIL import Image
# # # # # import io

# # # # # # ESP32-CAM IP address
# # # # # ESP32CAM_IP = "http://192.168.147.81/capture"
# # # # # SAVE_PATH = "captured_image.jpg"

# # # # # # Function to connect to the MySQL database
# # # # # def connect_db():
# # # # #     return mysql.connector.connect(
# # # # #         host="localhost",
# # # # #         user="root",
# # # # #         password="Indira@1943",
# # # # #         database="second_eye"
# # # # #     )

# # # # # # Function to announce audio message in a separate thread
# # # # # def announce(message):
# # # # #     def speak():
# # # # #         engine = pyttsx3.init()
# # # # #         engine.say(message)
# # # # #         engine.runAndWait()
    
# # # # #     thread = threading.Thread(target=speak)
# # # # #     thread.start()

# # # # # # Function to encode faces using face_recognition
# # # # # def encode_faces(image):
# # # # #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # # # #     face_locations = face_recognition.face_locations(rgb_image)
# # # # #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
# # # # #     return face_encodings, face_locations  # Return encodings + bounding box locations

# # # # # # Function to recognize faces and return individual matches
# # # # # def recognize_faces(captured_encodings):
# # # # #     conn = connect_db()
# # # # #     cursor = conn.cursor()
# # # # #     cursor.execute("SELECT image_name, image_data FROM images")
# # # # #     data = cursor.fetchall()
# # # # #     cursor.close()
# # # # #     conn.close()

# # # # #     face_results = []

# # # # #     for captured_encoding in captured_encodings:
# # # # #         best_match = "Unknown"
# # # # #         min_distance = 0.6

# # # # #         for image_name, image_blob in data:
# # # # #             stored_image = np.array(Image.open(io.BytesIO(image_blob)))
# # # # #             stored_encodings, _ = encode_faces(stored_image)

# # # # #             for stored_encoding in stored_encodings:
# # # # #                 distance = face_recognition.face_distance([stored_encoding], captured_encoding)[0]
# # # # #                 if distance < min_distance:
# # # # #                     min_distance = distance
# # # # #                     best_match = image_name
        
# # # # #         face_results.append(best_match)

# # # # #     return face_results

# # # # # # Function to upload image to the database
# # # # # def upload_image_to_db(image, image_name):
# # # # #     conn = connect_db()
# # # # #     cursor = conn.cursor()
# # # # #     image_bytes = io.BytesIO()
# # # # #     image.save(image_bytes, format='JPEG')
# # # # #     image_data = image_bytes.getvalue()
    
# # # # #     cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
# # # # #     conn.commit()
# # # # #     cursor.close()
# # # # #     conn.close()

# # # # # # Streamlit UI
# # # # # st.title("Second Eye - Image Recognition System 👁️👁️")

# # # # # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # # # # if page == "Home":
# # # # #     st.subheader("Welcome to the Home Page")

# # # # #     response = requests.get(ESP32CAM_IP)
# # # # #     if response.status_code == 200:
# # # # #         with open(SAVE_PATH, "wb") as file:
# # # # #             file.write(response.content)

# # # # #         captured_image = cv2.imread(SAVE_PATH)
# # # # #         captured_encodings, face_locations = encode_faces(captured_image)
# # # # #         captured_pil_image = Image.fromarray(cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB))
# # # # #         st.image(captured_pil_image, caption="Captured Image", use_column_width=True)

# # # # #         if captured_encodings:
# # # # #             match_results = recognize_faces(captured_encodings)
            
# # # # #             if len(match_results) == 1:
# # # # #                 name = match_results[0]
# # # # #                 announce(f"Single face detected: Match found with {name}")
# # # # #                 st.success(f"Single face detected: Match found with {name}")
# # # # #             else:
# # # # #                 for idx, name in enumerate(match_results, 1):
# # # # #                     announce(f"Face {idx}: Match found with {name}")
# # # # #                     st.success(f"Face {idx}: Match found with {name}")
# # # # #         else:
# # # # #             announce("No face detected in captured image")
# # # # #             st.warning("No face detected, but image displayed.")
    
# # # # #         os.remove(SAVE_PATH)
# # # # #     else:
# # # # #         st.error("Failed to capture image")
# # # # #         announce("Failed to capture image")

# # # # # elif page == "Supervisor":
# # # # #     st.subheader("Upload Image")
# # # # #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# # # # #     image_name = st.text_input("Enter Image Name")

# # # # #     if st.button("Upload") and uploaded_image and image_name:
# # # # #         image = Image.open(uploaded_image)
# # # # #         upload_image_to_db(image, image_name)
# # # # #         st.success("Image uploaded successfully!")

# # # # # elif page == "User":
# # # # #     st.subheader("Retrieve Images")
# # # # #     conn = connect_db()
# # # # #     cursor = conn.cursor()
# # # # #     cursor.execute("SELECT image_name, image_data FROM images")
# # # # #     images_data = cursor.fetchall()
# # # # #     cursor.close()
# # # # #     conn.close()

# # # # #     for image_name, image_blob in images_data:
# # # # #         image = Image.open(io.BytesIO(image_blob))
# # # # #         st.image(image, caption=image_name, use_column_width=True)


# # # # # ..BOX multiple

# # # import os
# # # import streamlit as st
# # # import mysql.connector
# # # import requests
# # # import face_recognition
# # # import os
# # # import pyttsx3
# # # import threading
# # # import cv2
# # # import numpy as np
# # # from PIL import Image
# # # import io

# # # # ESP32-CAM IP address
# # # ESP32CAM_IP = "http://192.168.147.81/capture"
# # # SAVE_PATH = "captured_image.jpg"

# # # # Function to connect to the MySQL database
# # # # def connect_db():
# # # #     return mysql.connector.connect(
# # # #         host="localhost",
# # # #         user="root",
# # # #         password="Indira@1943",
# # # #         database="second_eye"
# # # #     )

# # # # Function to connect to the Clever Cloud MySQL database
# # # def connect_db():
# # #     return mysql.connector.connect(
# # #         host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# # #         user="uulwfabkmrk4gxk2",
# # #         password="Indira@1943",  # Replace with your actual password
# # #         database="b1fvdoqarhekhvzuhdcj",
# # #         port=3306
# # #     )
    
# # # # Function to announce audio message in a separate thread
# # # def announce(message):
# # #     def speak():
# # #         engine = pyttsx3.init()
# # #         engine.say(message)
# # #         engine.runAndWait()
    
# # #     thread = threading.Thread(target=speak)
# # #     thread.start()

# # # # Function to encode faces using face_recognition
# # # def encode_faces(image):
# # #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # #     face_locations = face_recognition.face_locations(rgb_image)
# # #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
# # #     return face_encodings, face_locations  # Return encodings + bounding box locations

# # # # Function to recognize faces and return individual matches
# # # def recognize_faces(captured_encodings):
# # #     conn = connect_db()
# # #     cursor = conn.cursor()
# # #     cursor.execute("SELECT image_name, image_data FROM images")
# # #     data = cursor.fetchall()
# # #     cursor.close()
# # #     conn.close()

# # #     face_results = []

# # #     for captured_encoding in captured_encodings:
# # #         best_match = "Unknown"
# # #         min_distance = 0.6

# # #         for image_name, image_blob in data:
# # #             stored_image = np.array(Image.open(io.BytesIO(image_blob)))
# # #             stored_encodings, _ = encode_faces(stored_image)

# # #             for stored_encoding in stored_encodings:
# # #                 distance = face_recognition.face_distance([stored_encoding], captured_encoding)[0]
# # #                 if distance < min_distance:
# # #                     min_distance = distance
# # #                     best_match = image_name
        
# # #         face_results.append(best_match if best_match != "Unknown" else "Unknown Face")

# # #     return face_results

# # # # Function to draw bounding boxes and labels on image
# # # def draw_bounding_boxes(image, face_locations, match_results):
# # #     for (top, right, bottom, left), name in zip(face_locations, match_results):
# # #         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)  # Green box
# # #         cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# # #     return image

# # # # Function to upload image to the database
# # # def upload_image_to_db(image, image_name):
# # #     conn = connect_db()
# # #     cursor = conn.cursor()
# # #     image_bytes = io.BytesIO()
# # #     image.save(image_bytes, format='JPEG')
# # #     image_data = image_bytes.getvalue()
    
# # #     cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
# # #     conn.commit()
# # #     cursor.close()
# # #     conn.close()

# # # # Streamlit UI
# # # st.title("Second Eye - Image Recognition System 👁️👁️")

# # # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # # if page == "Home":
# # #     st.subheader("Welcome to the Home Page")

# # #     response = requests.get(ESP32CAM_IP)
# # #     if response.status_code == 200:
# # #         with open(SAVE_PATH, "wb") as file:
# # #             file.write(response.content)

# # #         captured_image = cv2.imread(SAVE_PATH)
# # #         captured_encodings, face_locations = encode_faces(captured_image)
        
# # #         if captured_encodings:
# # #             match_results = recognize_faces(captured_encodings)
            
# # #             # Draw bounding boxes with names
# # #             processed_image = draw_bounding_boxes(captured_image, face_locations, match_results)
# # #             processed_pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
# # #             st.image(processed_pil_image, caption="Processed Image with Matches", use_column_width=True)
            
# # #             for idx, name in enumerate(match_results, 1):
# # #                 if name == "Unknown Face":
# # #                     announce(f"Face {idx}: Not recognized")
# # #                     st.warning(f"Face {idx}: Not recognized")
# # #                 else:
# # #                     announce(f"Face {idx}: Match found with {name}")
# # #                     st.success(f"Face {idx}: Match found with {name}")
# # #         else:
# # #             captured_pil_image = Image.fromarray(cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB))
# # #             st.image(captured_pil_image, caption="Captured Image (No Faces Detected)", use_column_width=True)
# # #             announce("No face detected in captured image")
# # #             st.warning("No face detected, but image displayed.")
    
# # #         os.remove(SAVE_PATH)
# # #     else:
# # #         st.error("Failed to capture image")
# # #         announce("Failed to capture image")

# # # elif page == "Supervisor":
# # #     st.subheader("Upload Image")
# # #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# # #     image_name = st.text_input("Enter Image Name")

# # #     if st.button("Upload") and uploaded_image and image_name:
# # #         image = Image.open(uploaded_image)
# # #         upload_image_to_db(image, image_name)
# # #         st.success("Image uploaded successfully!")

# # # elif page == "User":
# # #     st.subheader("Retrieve Images")
# # #     conn = connect_db()
# # #     cursor = conn.cursor()
# # #     cursor.execute("SELECT image_name, image_data FROM images")
# # #     images_data = cursor.fetchall()
# # #     cursor.close()
# # #     conn.close()

# # #     for image_name, image_blob in images_data:
# # #         image = Image.open(io.BytesIO(image_blob))
# # #         st.image(image, caption=image_name, use_column_width=True)





# # # # import os
# # # # import streamlit as st
# # # # import MySQLdb

# # # # import requests
# # # # import face_recognition
# # # # import pyttsx3
# # # # import threading
# # # # import cv2
# # # # import numpy as np
# # # # from PIL import Image
# # # # import io

# # # # def install_dependencies():
# # # #     os.system("pip install mysql-connector-python==8.0.33")
# # # #     os.system("pip install face-recognition")
# # # #     os.system("pip install opencv-python numpy pillow pyttsx3 requests")

# # # # install_dependencies()

# # # # ESP32CAM_IP = "http://192.168.147.81/capture"
# # # # SAVE_PATH = "captured_image.jpg"

# # # # def connect_db():
# # # #     try:
# # # #         conn = mysql.connect(
# # # #             host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# # # #             user="uulwfabkmrk4gxk2",
# # # #             password="Indira@1943",
# # # #             database="b1fvdoqarhekhvzuhdcj",
# # # #             port=3306
# # # #         )
# # # #         return conn
# # # #     except mysql.Error as e:
# # # #         st.error(f"Database Connection Failed: {e}")
# # # #         return None


# # # # def announce(message):
# # # #     def speak():
# # # #         engine = pyttsx3.init()
# # # #         engine.say(message)
# # # #         engine.runAndWait()
# # # #     thread = threading.Thread(target=speak)
# # # #     thread.start()

# # # # def encode_faces(image):
# # # #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # # #     face_locations = face_recognition.face_locations(rgb_image)
# # # #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
# # # #     return face_encodings, face_locations

# # # # def recognize_faces(captured_encodings):
# # # #     conn = connect_db()
# # # #     if conn is None:
# # # #         return ["Database Error"]
# # # #     cursor = conn.cursor()
# # # #     cursor.execute("SELECT image_name, image_data FROM images")
# # # #     data = cursor.fetchall()
# # # #     cursor.close()
# # # #     conn.close()

# # # #     face_results = []
# # # #     for captured_encoding in captured_encodings:
# # # #         best_match = "Unknown"
# # # #         min_distance = 0.6
# # # #         for image_name, image_blob in data:
# # # #             stored_image = np.array(Image.open(io.BytesIO(image_blob)))
# # # #             stored_encodings, _ = encode_faces(stored_image)
# # # #             for stored_encoding in stored_encodings:
# # # #                 distance = face_recognition.face_distance([stored_encoding], captured_encoding)[0]
# # # #                 if distance < min_distance:
# # # #                     min_distance = distance
# # # #                     best_match = image_name
# # # #         face_results.append(best_match if best_match != "Unknown" else "Unknown Face")
# # # #     return face_results

# # # # def draw_bounding_boxes(image, face_locations, match_results):
# # # #     for (top, right, bottom, left), name in zip(face_locations, match_results):
# # # #         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
# # # #         cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# # # #     return image

# # # # def upload_image_to_db(image, image_name):
# # # #     conn = connect_db()
# # # #     if conn is None:
# # # #         return
# # # #     cursor = conn.cursor()
# # # #     image_bytes = io.BytesIO()
# # # #     image.save(image_bytes, format='JPEG')
# # # #     image_data = image_bytes.getvalue()
# # # #     cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
# # # #     conn.commit()
# # # #     cursor.close()
# # # #     conn.close()

# # # # st.title("Second Eye - Image Recognition System 👁️👁️")
# # # # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # # # if page == "Home":
# # # #     st.subheader("Welcome to the Home Page")
# # # #     response = requests.get(ESP32CAM_IP)
# # # #     if response.status_code == 200:
# # # #         with open(SAVE_PATH, "wb") as file:
# # # #             file.write(response.content)
# # # #         captured_image = cv2.imread(SAVE_PATH)
# # # #         captured_encodings, face_locations = encode_faces(captured_image)
# # # #         if captured_encodings:
# # # #             match_results = recognize_faces(captured_encodings)
# # # #             processed_image = draw_bounding_boxes(captured_image, face_locations, match_results)
# # # #             processed_pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
# # # #             st.image(processed_pil_image, caption="Processed Image with Matches", use_column_width=True)
# # # #             for idx, name in enumerate(match_results, 1):
# # # #                 if name == "Unknown Face":
# # # #                     announce(f"Face {idx}: Not recognized")
# # # #                     st.warning(f"Face {idx}: Not recognized")
# # # #                 else:
# # # #                     announce(f"Face {idx}: Match found with {name}")
# # # #                     st.success(f"Face {idx}: Match found with {name}")
# # # #         else:
# # # #             st.warning("No face detected in captured image")
# # # #         os.remove(SAVE_PATH)
# # # #     else:
# # # #         st.error("Failed to capture image")

# # # # elif page == "Supervisor":
# # # #     st.subheader("Upload Image")
# # # #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# # # #     image_name = st.text_input("Enter Image Name")
# # # #     if st.button("Upload") and uploaded_image and image_name:
# # # #         image = Image.open(uploaded_image)
# # # #         upload_image_to_db(image, image_name)
# # # #         st.success("Image uploaded successfully!")

# # # # elif page == "User":
# # # #     st.subheader("Retrieve Images")
# # # #     conn = connect_db()
# # # #     if conn is not None:
# # # #         cursor = conn.cursor()
# # # #         cursor.execute("SELECT image_name, image_data FROM images")
# # # #         images_data = cursor.fetchall()
# # # #         cursor.close()
# # # #         conn.close()
# # # #         for image_name, image_blob in images_data:
# # # #             image = Image.open(io.BytesIO(image_blob))
# # # #             st.image(image, caption=image_name, use_column_width=True)





# # # # import os
# # # # import streamlit as st
# # # # import mysql.connector  
# # # # import requests
# # # # import face_recognition
# # # # import pyttsx3
# # # # import threading
# # # # import cv2
# # # # import numpy as np
# # # # from PIL import Image
# # # # import io

# # # # ESP32CAM_IP = "http://192.168.147.81/capture"
# # # # SAVE_PATH = "captured_image.jpg"

# # # # <<<<<<< HEAD
# # # # # Function to connect to the MySQL database
# # # # def connect_db():
# # # #     return mysql.connector.connect(
# # # #         host="localhost",
# # # #         user="root",
# # # #         password="Indira@1943",
# # # #         database="second_eye"
# # # #     )

# # # # # Function to connect to the Clever Cloud MySQL database
# # # # # def connect_db():
# # # # #     return mysql.connector.connect(
# # # # #         host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# # # # #         user="uulwfabkmrk4gxk2",
# # # # #         password="Indira@1943",  # Replace with your actual password
# # # # #         database="b1fvdoqarhekhvzuhdcj",
# # # # #         port=3306
# # # # #     )

# # # # # Function to announce audio message in a separate thread
# # # # =======


# # # # def connect_db():
# # # #     try:
# # # #         conn = mysql.connector.connect(  # Use mysql.connector
# # # #             host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# # # #             user="uulwfabkmrk4gxk2",
# # # #             password="Indira@1943",
# # # #             database="b1fvdoqarhekhvzuhdcj",
# # # #             port=3306
# # # #         )
# # # #         return conn
# # # #     except mysql.connector.Error as e:
# # # #         st.error(f"Database Connection Failed: {e}")
# # # #         return None


# # # # >>>>>>> origin/master
# # # # def announce(message):
# # # #     def speak():
# # # #         engine = pyttsx3.init()
# # # #         engine.say(message)
# # # #         engine.runAndWait()
# # # #     threading.Thread(target=speak).start()

# # # # def encode_faces(image):
# # # #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # # #     face_locations = face_recognition.face_locations(rgb_image)
# # # #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
# # # #     return face_encodings, face_locations

# # # # def recognize_faces(captured_encodings):
# # # #     conn = connect_db()
# # # #     if conn is None:
# # # #         return ["Database Error"]

# # # #     with conn.cursor() as cursor:  # ✅ Using "with" to auto-close cursor
# # # #         cursor.execute("SELECT image_name, image_data FROM images")
# # # #         data = cursor.fetchall()

# # # #     conn.close()

# # # #     face_results = []
# # # #     for captured_encoding in captured_encodings:
# # # #         best_match = "Unknown"
# # # #         min_distance = 0.6
# # # #         for image_name, image_blob in data:
# # # #             stored_image = np.array(Image.open(io.BytesIO(image_blob)))
# # # #             stored_encodings, _ = encode_faces(stored_image)
# # # #             for stored_encoding in stored_encodings:
# # # #                 distance = face_recognition.face_distance([stored_encoding], captured_encoding)[0]
# # # #                 if distance < min_distance:
# # # #                     min_distance = distance
# # # #                     best_match = image_name
# # # #         face_results.append(best_match if best_match != "Unknown" else "Unknown Face")
    
# # # #     return face_results

# # # # def draw_bounding_boxes(image, face_locations, match_results):
# # # #     for (top, right, bottom, left), name in zip(face_locations, match_results):
# # # #         cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
# # # #         cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# # # #     return image

# # # # def upload_image_to_db(image, image_name):
# # # #     conn = connect_db()
# # # #     if conn is None:
# # # #         return

# # # #     with conn.cursor() as cursor:
# # # #         image_bytes = io.BytesIO()
# # # #         image.save(image_bytes, format='JPEG')
# # # #         image_data = image_bytes.getvalue()
# # # #         cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
# # # #         conn.commit()

# # # #     conn.close()

# # # # st.title("Second Eye - Image Recognition System 👁️👁️")
# # # # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # # # if page == "Home":
# # # #     st.subheader("Welcome to the Home Page")
    
# # # #     try:
# # # #         response = requests.get(ESP32CAM_IP, timeout=5)
# # # #         if response.status_code == 200:
# # # #             with open(SAVE_PATH, "wb") as file:
# # # #                 file.write(response.content)
# # # #             captured_image = cv2.imread(SAVE_PATH)
# # # #             captured_encodings, face_locations = encode_faces(captured_image)
# # # #             if captured_encodings:
# # # #                 match_results = recognize_faces(captured_encodings)
# # # #                 processed_image = draw_bounding_boxes(captured_image, face_locations, match_results)
# # # #                 processed_pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
# # # #                 st.image(processed_pil_image, caption="Processed Image with Matches", use_column_width=True)
# # # #                 for idx, name in enumerate(match_results, 1):
# # # #                     if name == "Unknown Face":
# # # #                         announce(f"Face {idx}: Not recognized")
# # # #                         st.warning(f"Face {idx}: Not recognized")
# # # #                     else:
# # # #                         announce(f"Face {idx}: Match found with {name}")
# # # #                         st.success(f"Face {idx}: Match found with {name}")
# # # #             else:
# # # #                 st.warning("No face detected in captured image")
# # # #             os.remove(SAVE_PATH)
# # # #         else:
# # # #             st.error("Failed to capture image")
# # # #     except requests.exceptions.RequestException as e:
# # # #         st.error(f"Error connecting to camera: {e}")

# # # # elif page == "Supervisor":
# # # #     st.subheader("Upload Image")
# # # #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# # # #     image_name = st.text_input("Enter Image Name")
# # # #     if st.button("Upload") and uploaded_image and image_name:
# # # #         image = Image.open(uploaded_image)
# # # #         upload_image_to_db(image, image_name)
# # # #         st.success("Image uploaded successfully!")

# # # # elif page == "User":
# # # #     st.subheader("Retrieve Images")
# # # #     conn = connect_db()
# # # #     if conn is not None:
# # # #         with conn.cursor() as cursor:
# # # #             cursor.execute("SELECT image_name, image_data FROM images")
# # # #             images_data = cursor.fetchall()
        
# # # #         conn.close()

# # # #         for image_name, image_blob in images_data:
# # # #             image = Image.open(io.BytesIO(image_blob))
# # # #             st.image(image, caption=image_name, use_column_width=True)





# # import os
# # import streamlit as st
# # import mysql.connector
# # import requests
# # from deepface import DeepFace
# # import pyttsx3
# # import threading
# # import cv2
# # import numpy as np
# # from PIL import Image
# # import io

# # # ESP32-CAM IP address
# # ESP32CAM_IP = "http://192.168.147.81/capture"
# # SAVE_PATH = "captured_image.jpg"

# # # Function to connect to the MySQL database
# # def connect_db():
# #     return mysql.connector.connect(
# #         host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# #         user="uulwfabkmrk4gxk2",
# #         password="Indira@1943",  # Replace with your actual password
# #         database="b1fvdoqarhekhvzuhdcj",
# #         port=3306
# #     )

# # # Function to announce audio message in a separate thread
# # def announce(message):
# #     def speak():
# #         engine = pyttsx3.init()
# #         engine.say(message)
# #         engine.runAndWait()
# #     thread = threading.Thread(target=speak)
# #     thread.start()

# # # Function to recognize faces using DeepFace
# # def recognize_faces(captured_image):
# #     conn = connect_db()
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT image_name, image_data FROM images")
# #     data = cursor.fetchall()
# #     cursor.close()
# #     conn.close()

# #     face_results = []
    
# #     for image_name, image_blob in data:
# #         stored_image = Image.open(io.BytesIO(image_blob))
        
# #         try:
# #             result = DeepFace.verify(np.array(stored_image), np.array(captured_image))
# #             if result["verified"]:
# #                 face_results.append(image_name)
# #             else:
# #                 face_results.append("Unknown Face")
# #         except:
# #             face_results.append("Error Processing Image")
    
# #     return face_results

# # # Function to upload image to the database
# # def upload_image_to_db(image, image_name):
# #     conn = connect_db()
# #     cursor = conn.cursor()
# #     image_bytes = io.BytesIO()
# #     image.save(image_bytes, format='JPEG')
# #     image_data = image_bytes.getvalue()
    
# #     cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
# #     conn.commit()
# #     cursor.close()
# #     conn.close()

# # # Streamlit UI
# # st.title("Second Eye - Image Recognition System 👁️👁️")

# # page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# # if page == "Home":
# #     st.subheader("Welcome to the Home Page")

# #     response = requests.get(ESP32CAM_IP)
# #     if response.status_code == 200:
# #         with open(SAVE_PATH, "wb") as file:
# #             file.write(response.content)

# #         captured_image = Image.open(SAVE_PATH)
# #         match_results = recognize_faces(np.array(captured_image))
        
# #         st.image(captured_image, caption="Captured Image", use_column_width=True)
        
# #         for idx, name in enumerate(match_results, 1):
# #             if name == "Unknown Face":
# #                 announce(f"Face {idx}: Not recognized")
# #                 st.warning(f"Face {idx}: Not recognized")
# #             else:
# #                 announce(f"Face {idx}: Match found with {name}")
# #                 st.success(f"Face {idx}: Match found with {name}")
# #     else:
# #         st.error("Failed to capture image")
# #         announce("Failed to capture image")

# # elif page == "Supervisor":
# #     st.subheader("Upload Image")
# #     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
# #     image_name = st.text_input("Enter Image Name")

# #     if st.button("Upload") and uploaded_image and image_name:
# #         image = Image.open(uploaded_image)
# #         upload_image_to_db(image, image_name)
# #         st.success("Image uploaded successfully!")

# # elif page == "User":
# #     st.subheader("Retrieve Images")
# #     conn = connect_db()
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT image_name, image_data FROM images")
# #     images_data = cursor.fetchall()
# #     cursor.close()
# #     conn.close()

# #     for image_name, image_blob in images_data:
# #         image = Image.open(io.BytesIO(image_blob))
# #         st.image(image, caption=image_name, use_column_width=True)





# import os
# import streamlit as st
# import mysql.connector
# import requests
# import pyttsx3
# import threading
# import cv2
# import numpy as np
# from PIL import Image
# import io

# # ESP32-CAM IP address
# ESP32CAM_IP = "http://192.168.147.81/capture"
# SAVE_PATH = "captured_image.jpg"

# # Function to connect to the Clever Cloud MySQL database
# # Function to connect to the Clever Cloud MySQL database
# # def connect_db():
# #     return mysql.connector.connect(
# #         host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",
# #         user="uulwfabkmrk4gxk2",
# #         password="raD83QmPrQNbBRFHvRj7",  # Updated password
# #         database="b1fvdoqarhekhvzuhdcj",
# #         port=3306
# #     )
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Indira@1943",
#         database="second_eye"
#     )

# # Function to announce audio message in a separate thread
# def announce(message):
#     def speak():
#         engine = pyttsx3.init()
#         engine.say(message)
#         engine.runAndWait()
    
#     thread = threading.Thread(target=speak)
#     thread.start()

# # Streamlit UI
# st.title("Second Eye - Image Recognition System 👁️👁️")

# page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

# if page == "Home":
#     st.subheader("Welcome to the Home Page")
#     response = requests.get(ESP32CAM_IP)
#     if response.status_code == 200:
#         with open(SAVE_PATH, "wb") as file:
#             file.write(response.content)
#         captured_image = Image.open(SAVE_PATH)
#         st.image(captured_image, caption="Captured Image", use_column_width=True)
#         os.remove(SAVE_PATH)
#     else:
#         st.error("Failed to capture image")
#         announce("Failed to capture image")

# elif page == "Supervisor":
#     st.subheader("Upload Image")
#     uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
#     image_name = st.text_input("Enter Image Name")

#     if st.button("Upload") and uploaded_image and image_name:
#         image = Image.open(uploaded_image)
#         upload_image_to_db(image, image_name)
#         st.success("Image uploaded successfully!")

# elif page == "User":
#     st.subheader("Retrieve Images")
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT image_name, image_data FROM images")
#     images_data = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     for image_name, image_blob in images_data:
#         image = Image.open(io.BytesIO(image_blob))
#         st.image(image, caption=image_name, use_column_width=True)

# # Handle the port for Render deployment
# if __name__ == "__main__":
#     PORT = os.getenv("PORT", "8501")
#     os.system(f"streamlit run {__file__} --server.port={PORT} --server.address=0.0.0.0")



import os
import streamlit as st
import mysql.connector
import requests
import pyttsx3
import threading
import cv2
import numpy as np
from PIL import Image
import io

# ESP32-CAM IP address
ESP32CAM_IP = "http://192.168.147.81/capture"
SAVE_PATH = "captured_image.jpg"

# Function to connect to the Clever Cloud MySQL database
def connect_db():
    return mysql.connector.connect(
        host="b1fvdoqarhekhvzuhdcj-mysql.services.clever-cloud.com",  # ✅ Clever Cloud host
        user="root",
        password="Indira@1943",  # ✅ Use correct password
        database="second_eye",  # ✅ Use correct DB name
        port=3306
    )

# Function to upload image to MySQL database
def upload_image_to_db(image, image_name):
    conn = connect_db()
    cursor = conn.cursor()
    
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_data = image_bytes.getvalue()
    
    cursor.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (image_name, image_data))
    conn.commit()
    cursor.close()
    conn.close()

# Function to announce audio message in a separate thread
def announce(message):
    def speak():
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    
    thread = threading.Thread(target=speak)
    thread.start()

# Streamlit UI
st.title("Second Eye - Image Recognition System 👁️👁️")

page = st.sidebar.selectbox("Select Page", ["Home", "Supervisor", "User"])

if page == "Home":
    st.subheader("Welcome to the Home Page")
    response = requests.get(ESP32CAM_IP)
    if response.status_code == 200:
        with open(SAVE_PATH, "wb") as file:
            file.write(response.content)
        captured_image = Image.open(SAVE_PATH)
        st.image(captured_image, caption="Captured Image", use_column_width=True)
        os.remove(SAVE_PATH)
    else:
        st.error("Failed to capture image")
        announce("Failed to capture image")

elif page == "Supervisor":
    st.subheader("Upload Image")
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    image_name = st.text_input("Enter Image Name")

    if st.button("Upload") and uploaded_image and image_name:
        image = Image.open(uploaded_image)
        upload_image_to_db(image, image_name)
        st.success("Image uploaded successfully!")

elif page == "User":
    st.subheader("Retrieve Images")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT image_name, image_data FROM images")
    images_data = cursor.fetchall()
    cursor.close()
    conn.close()

    for image_name, image_blob in images_data:
        image = Image.open(io.BytesIO(image_blob))
        st.image(image, caption=image_name, use_column_width=True)

# Handle the port for Render deployment
if __name__ == "__main__":
    st.write("Running on Render with PORT:", os.getenv("PORT", "8501"))
