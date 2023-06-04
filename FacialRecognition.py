import cv2
import mediapipe as mp
import math
import numpy as np

def capture_direction_and_gesture():
    mp_drawing = mp.solutions.drawing_utils
    #Deteccion de rostros
    mp_facemesh = mp.solutions.face_mesh

    #Deteccion de manos (para los gestos)
    hand_tracking = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

    cap = cv2.VideoCapture(0)

    with mp_facemesh.FaceMesh() as face_mesh:
        while True:
            #Leemos el video de la webcam
            ret, frame = cap.read()
            if not ret:
                #Si ya no recibimos más video, se rompe el ciclo
                break

            #Convertimos el frame a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #Le pasamos los frames a face_mesh y guardamos el resultado
            results = face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    rango_superior = 0.40
                    rango_inferior = 0.35

                    threshold = 0.05
                    # Obtener las coordenadas de los puntos clave relevantes
                    left_eye_x = face_landmarks.landmark[33].x  # Punto clave del ojo izquierdo
                    right_eye_x = face_landmarks.landmark[263].x  # Punto clave del ojo derecho

                    # Obtener las coordenadas de los puntos clave relevantes para la dirección vertical
                    left_eye_y = face_landmarks.landmark[33].y  # Punto clave del ojo izquierdo
                    right_eye_y = face_landmarks.landmark[263].y  # Punto clave del ojo derecho
                    nose_y = face_landmarks.landmark[168].y  # Punto clave de la nariz

                    # Definir umbrales para la detección de dirección horizontal
                    umbral_derecha = 0.5954259300231934
                    umbral_izquierda = 0.3254942297935486

                    # Determinar la dirección vertical
                    #print("Nariz:", nose_y)
                    #print("ojos: ", (left_eye_y + right_eye_y) / 2)
                    if nose_y > (left_eye_y + right_eye_y) / 2:
                        if nose_y > rango_superior:
                            direction_vertical = "Abajo"
                        else:
                            direction_vertical = "Frente"
                    elif nose_y < (left_eye_y + right_eye_y) / 2:
                        if nose_y < rango_inferior:
                            direction_vertical = "Arriba"
                        else:
                            direction_vertical = "Frente"
                    else:
                        direction_vertical = "Frente"

                    # Determinar la dirección horizontal
                    #print("Ojo derecho: ", right_eye_x)
                    #print("Ojo izquierdo: ", left_eye_x)
                    #print("Umbral izq: ", umbral_izquierda)
                    #print("Umbral dere:", umbral_derecha)
                    if right_eye_x > umbral_derecha:
                        direction_horizontal = "Izquierda"
                    elif left_eye_x < umbral_izquierda:
                        direction_horizontal = "Derecha"
                    else:
                        direction_horizontal = "Frente"


                    # Determinar la dirección final
                    if direction_horizontal == "Frente" and direction_vertical == "Frente":
                        direction = "Frente"
                    elif direction_horizontal != "Frente" and direction_vertical == "Frente":
                        direction = direction_horizontal
                    elif direction_horizontal == "Frente" and direction_vertical != "Frente":
                        direction = direction_vertical
                    else:
                        # Aqui ganará la direccion vertical
                        direction = direction_vertical

                    # Dibujar los puntos clave en el marco
                    mp_drawing.draw_landmarks(frame, face_landmarks, mp_facemesh.FACEMESH_CONTOURS,
                                              mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                                              mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1))

                    # Mostrar la dirección en la pantalla
                    cv2.putText(frame, f"Direccion: {direction}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #here
            # Procesar el frame con Mediapipe para el seguimiento de manos
            results = hand_tracking.process(frame_rgb)

            # Inicializar gesture_text con un valor predeterminado
            gesture_text = "No detectado"

            # Comprobar si se detectaron manos
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Detectar gesto de pistola
                    thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                    index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
                    ring_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
                    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
                    index_finger_dip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_DIP]
                    pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]

                    thumb_x, thumb_y = int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0])
                    index_x, index_y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])
                    middle_x, middle_y = int(middle_finger_tip.x * frame.shape[1]), int(middle_finger_tip.y * frame.shape[0])
                    ring_x, ring_y = int(ring_finger_tip.x * frame.shape[1]), int(ring_finger_tip.y * frame.shape[0])
                    wrist_x, wrist_y = int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0])
                    index_dip_x, index_dip_y = int(index_finger_dip.x * frame.shape[1]), int(index_finger_dip.y * frame.shape[0])
                    pinky_x, pinky_y = int(pinky_tip.x * frame.shape[1]), int(pinky_tip.y * frame.shape[0])

                    # Calcular la dirección del gesto
                    gesture_direction = math.atan2(index_y - wrist_y, index_x - wrist_x)
                    angle_threshold = 0.35 
                    threshold = 50

                   # Verificar el gesto de pistola izquierda
                    if thumb_x < index_x and gesture_direction < -angle_threshold:
                        direction = "Izquierda"
                        gesture_text = "Pistola"

                    # Detectar gesto de pulgar hacia arriba
                    if thumb_y < index_y and thumb_y < middle_y and thumb_y < ring_y and thumb_y < pinky_y:
                        direction = "Arriba"
                        gesture_text = "Pulgar hacia arriba (Granada)"

                    # Detectar gesto de dos dedos horizontales
                    if index_x < middle_x and math.sqrt((index_x - middle_x)**2 + (index_y - middle_y)**2) > threshold:
                        direction = "Horizontal"
                        gesture_text = "Dos dedos horizontales (Fusil)"

                    cv2.putText(frame, f"Arma: {gesture_text}", (30, 64), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    #Estetica

                    # Dibujar los puntos de referencia de las manos
                    for landmark in hand_landmarks.landmark:
                        x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                        
                    # Dibujar las conexiones entre los puntos de referencia de las manos
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            cv2.imshow('Facemesh', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return direction, gesture_text

    cap.release()
    cv2.destroyAllWindows()

#direction, gesture = capture_direction_and_gesture()
#print(direction)
#print(gesture)