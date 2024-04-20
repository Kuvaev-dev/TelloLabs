import pygame
from djitellopy import Tello
import numpy as np 
import cv2 
import mediapipe as mp
import threading # завантажуємо threding для асинхронного виконання

# Імпорт класів та типів з бібліотеки Mediapipe для використання FaceDetector
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Шлях до моделі розпізнавання обличчя
MODEL_PATH = 'level-2/blaze_face_short_range.tflite'

# Функція для відображення обличчя на кадрі
def render_frame(result, output_image, timestamp_ms):
    
    frame = output_image.numpy_view()

    # Перевірка наявності обличчя на кадрі
    if result.detections:
        for detection in result.detections:
            bbox = detection.bounding_box
            # Намалювати прямокутник навколо обличчя
            cv2.rectangle(
                frame,
                (bbox.origin_x, bbox.origin_y),
                (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height),
                color=(255, 0, 0),
                thickness=2
            )
            # Обчислення центру обличчя
            face_center = bbox.origin_x + bbox.width // 2
        if is_tracking:
            track_face(face_center)

    # Обертання кадру та конвертація для відображення в Pygame
    frame = np.rot90(frame)
    frame = np.flipud(frame) 
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))

# Функція для слідкування за обличчям
def track_face(face_center):
    error = FRAME_CENTER - face_center
    yaw_velocity = int(Kp * error)
    # Відправка команди до дрона для слідкування за обличчям
    drone.send_rc_control(0, 0, 0, yaw_velocity)

# Налаштування параметрів для FaceDetector
options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=render_frame
)

# Розміри вікна Pygame
WIDTH = 960
HEIGHT = 720
FRAME_CENTER = WIDTH / 2

# Ініціалізація Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 30 
clock = pygame.time.Clock() 

# Ініціалізація дрона та підключення
drone = Tello()
drone.connect()
drone.streamon()
frame_read = drone.get_frame_read()

# Глобальні змінні для статусу дрона та слідкування
is_flying = False # статус дрона, True -- в польоті, False -- на землі
is_tracking = False

# Коефіцієнт пропорційної регуляції для слідкування за обличчям
Kp = -0.125

timestamp = 0
is_running = True

# Ініціалізація FaceDetector та головного циклу
with FaceDetector.create_from_options(options) as detector:
    while is_running: 
        # Обробка подій Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Посадка дрона та вимкнення стрімування при закритті вікна
                if is_flying: 
                    threading.Thread(target=drone.land).start()
                    is_tracking = False
                    is_flying = False
                drone.streamoff()
                is_running = False
            # Обробка натискань клавіш
            if event.type == pygame.KEYDOWN:
                # Включення режиму слідкування
                if event.key == pygame.K_1 and is_flying:
                    is_tracking = True
                # Вимкнення режиму слідкування
                if event.key == pygame.K_0:
                    is_tracking = False
                    if is_flying:
                        drone.send_rc_control(0, 0, 0, 0)
                # Зліт дрона
                if event.key == pygame.K_t and not(is_flying):
                    is_flying = True
                    threading.Thread(target=drone.takeoff).start()
                # Посадка дрона
                if event.key == pygame.K_l and is_flying:
                    drone.send_rc_control(0, 0, 0, 0)
                    is_flying = False
                    is_tracking = False
                    threading.Thread(target=drone.land).start()

        # Отримання кадру відео з дрона
        frame = frame_read.frame 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Перетворення кадру для розпізнавання жестів
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Асинхронне розпізнавання обличчя
        detector.detect_async(mp_image, timestamp)

        timestamp += 1

        pygame.display.flip() 
        clock.tick(FPS)
