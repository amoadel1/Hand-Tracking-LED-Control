import cv2
import mediapipe as mp
import requests

# ESP32 IP Address
ESP32_IP = "10.246.151.160"

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Open camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Previous value
last_leds = -1

while True:

    # Read frame
    success, frame = cap.read()

    # Skip bad frames
    if not success:
        continue

    # Mirror image
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect hand
    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            # Draw hand landmarks
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            # Thumb tip
            thumb = hand.landmark[4]

            # Index tip
            index = hand.landmark[8]

            # Frame size
            h, w, c = frame.shape

            # Thumb coordinates
            x1 = int(thumb.x * w)
            y1 = int(thumb.y * h)

            # Index coordinates
            x2 = int(index.x * w)
            y2 = int(index.y * h)

            # Draw circles
            cv2.circle(frame, (x1, y1), 10, (0, 255, 0), -1)
            cv2.circle(frame, (x2, y2), 10, (0, 255, 0), -1)

            # Draw line
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

            # Calculate distance
            distance = int(
                ((x2 - x1) ** 2 +
                 (y2 - y1) ** 2) ** 0.5
            )

            # Convert distance to LEDs
            leds = int(distance / 5)

            # Limit to 0 - 30 LEDs
            leds = max(0, min(30, leds))

            # Show distance
            cv2.putText(
                frame,
                f"Distance: {distance}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Show LEDs value
            cv2.putText(
                frame,
                f"LEDs: {leds}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

            # Send only if changed
            if leds != last_leds:

                try:

                    url = f"http://{ESP32_IP}/value?d={leds}"

                    print("=" * 40)
                    print("Sending:", url)
                    print("Distance =", distance)
                    print("LEDs =", leds)

                    response = requests.get(
                        url,
                        timeout=1
                    )

                    print("ESP32 Response =", response.text)

                    last_leds = leds

                except Exception as e:

                    print("ESP32 ERROR:")
                    print(e)

    # Show video
    cv2.imshow(
        "Hand Tracking",
        frame
    )

    # ESC to exit
    key = cv2.waitKey(1)

    if key == 27:
        print("Program Stopped")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()