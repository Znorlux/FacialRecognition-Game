import mediapipe as mp
import cv2
import math
import numpy as np

def capture_direction_and_gesture():
    # Detección de caras
    face_detection = mp.solutions.face_detection.FaceDetection()

    # Seguimiento de manos
    hand_tracking = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

    video_capture = cv2.VideoCapture(0)

    while True:
        # Leer el video desde la webcam
        ret, frame = video_capture.read()

        # Convertir el frame a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar el frame con Mediapipe para la detección de caras
        result = face_detection.process(frame_rgb)

        # Obtener los resultados de la detección de caras
        if result.detections:
            for detection in result.detections:
                # Obtener la posición y la puntuación de la cara detectada
                bbox = detection.location_data.relative_bounding_box
                x, y, w, h = int(bbox.xmin * frame.shape[1]), int(bbox.ymin * frame.shape[0]), \
                            int(bbox.width * frame.shape[1]), int(bbox.height * frame.shape[0])

                # Calcular el centro de la cara
                center_x = x + w // 2
                center_y = y + h // 2

                # Calcular el centro del frame
                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2

                # Determinar la dirección hacia la que mira la cara
                direction = ""
                if center_x < frame_center_x - 35:
                    direction = "Derecha"
                elif center_x > frame_center_x + 25:
                    direction = "Izquierda"
                elif center_y < frame_center_y - 30:
                    direction = "Arriba"
                elif center_y > frame_center_y + 50:
                    direction = "Abajo"
                elif frame_center_x - 30 <= center_x <= frame_center_x + 30 and frame_center_y - 40 <= center_y <= frame_center_y + 50:
                    direction = "Frente"

                # Dibujar un rectángulo alrededor de la cara detectada
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Mostrar la dirección hacia la que mira la cara
                cv2.putText(frame, direction, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Obtener los puntos de referencia de la cara
                keypoints = detection.location_data.relative_keypoints

                # Obtener las coordenadas de los puntos de referencia para el enmascaramiento
                mask_coordinates = [
                    (int(keypoints[0].x * frame.shape[1]), int(keypoints[0].y * frame.shape[0])),  # Ojo izquierdo
                    (int(keypoints[1].x * frame.shape[1]), int(keypoints[1].y * frame.shape[0])),  # Ojo derecho
                    (int(keypoints[2].x * frame.shape[1]), int(keypoints[2].y * frame.shape[0])),  # Nariz
                    (int(keypoints[3].x * frame.shape[1]), int(keypoints[3].y * frame.shape[0])),  # Labio superior
                    (int(keypoints[4].x * frame.shape[1]), int(keypoints[4].y * frame.shape[0]))   # Labio inferior
                ]

                # Obtener las coordenadas de los puntos de referencia para los labios
                mouth_coordinates = [
                    (int(keypoints[3].x * frame.shape[1]), int(keypoints[3].y * frame.shape[0])),  # Boca izquierda
                    #(int(keypoints[4].x * frame.shape[1]), int(keypoints[4].y * frame.shape[0]))   # Boca derecha
                ]

                # Dibujar los puntos de referencia de la cara
                for keypoint in keypoints:
                    x, y = int(keypoint.x * frame.shape[1]), int(keypoint.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Dibujar los labios
                cv2.polylines(frame, [np.array(mouth_coordinates)], isClosed=True, color=(0, 255, 0), thickness=2)

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
                angle_threshold = 0.35  # Ajusta este umbral según tus necesidades
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

                cv2.putText(frame, gesture_text, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                #Estetica
                # Dibujar los puntos de referencia de las manos
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                # Dibujar las conexiones entre los puntos de referencia de las manos
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        # Mostrar el frame procesado
        cv2.imshow('Webcam', frame)

        # Detener el bucle al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Devolver la información de dirección y gesto
            return direction, gesture_text

    # Liberar la captura de video y cerrar las ventanas
    video_capture.release()
    cv2.destroyAllWindows()

#direction, gesture = capture_direction_and_gesture()
#print("Dirección: ", direction)
#print("Gesto: ", gesture)