import cv2
import mediapipe as mp

#Unirlo con el detector de manos y juego terminado
mp_drawing = mp.solutions.drawing_utils
mp_facemesh = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)

with mp_facemesh.FaceMesh() as face_mesh:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
                cv2.putText(frame, f"Direccion: {direction}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Facemesh', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
