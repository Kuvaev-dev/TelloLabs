# Імпорт необхідних модулів і бібліотек
import pygame
from djitellopy import Tello
import numpy as np 
import cv2 
import mediapipe as mp 
from helpers import draw_landmarks  # імпорт допоміжної функції для відображення ключових точок

# Імпорт класів та типів з бібліотеки Mediapipe для розпізнавання жестів
BaseOptions = mp.tasks.BaseOptions 
GestureRecognizer = mp.tasks.vision.GestureRecognizer 
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions 
VisionRunningMode = mp.tasks.vision.RunningMode 

# Шлях до моделі розпізнавання жестів
MODEL_PATH = 'level-1/gesture_recognizer.task'

# Функція для відображення результатів розпізнавання
def render_frame(result, output_image, timestamp_ms):
    global is_flying  # Глобальна змінна для відстеження стану польоту дрона

    # Відображення ключових точок на вихідному зображенні
    frame = draw_landmarks(output_image.numpy_view(), result)

    # Обертання та відображення кадру за допомогою Pygame
    frame = np.rot90(frame)
    frame = np.flipud(frame) 
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))

    # Перевірка наявності розпізнаних жестів
    if result.gestures:
        for gesture in result.gestures:
            print(gesture[0].category_name)  # Виведення назви розпізнаного жесту

            # Перевірка жесту та стану польоту для посадки дрона
            if gesture[0].category_name == "Open_Palm" and is_flying:
                threading.Thread(target=drone.land).start()
                is_flying = False

# Налаштування параметрів розпізнавання жестів
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM, 
    result_callback=render_frame 
)

# Налаштування розмірів вікна Pygame
WIDTH = 320
HEIGHT = 240

# Ініціалізація Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Налаштування FPS і годинника для керування частотою оновлення
FPS = 5 
clock = pygame.time.Clock() 

# Ініціалізація дрона та підключення до нього
drone = Tello()
drone.connect()

# Налаштування напрямку стріму відео та включення стріму
drone.set_video_direction(Tello.CAMERA_DOWNWARD)
drone.streamon()
frame_read = drone.get_frame_read()

# Глобальна змінна для відстеження стану польоту дрона
is_flying = False 

# Ініціалізація таймштампу та змінної для керування циклом
timestamp = 0 
is_running = True

# Запуск розпізнавання жестів
with GestureRecognizer.create_from_options(options) as recognizer:
    while is_running: 
        # Обробка подій Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if is_flying: 
                    threading.Thread(target=drone.land).start()
                    is_flying = False
                drone.streamoff()
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and not(is_flying):
                    is_flying = True
                    threading.Thread(target=drone.takeoff).start()
                if event.key == pygame.K_l and is_flying:
                    is_flying = False
                    threading.Thread(target=drone.land).start()

        # Отримання кадру від дрона
        frame = frame_read.frame 

        # Обрізка кадру до 240 пікселів висоти
        frame = frame[:240, :, :]

        # Перетворення кадру для розпізнавання
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Асинхронне розпізнавання жестів
        recognizer.recognize_async(
            mp_image,
            timestamp 
        )

        # Інкремент таймштампу
        timestamp += 1 

        # Оновлення екрану Pygame
        pygame.display.flip() 
        clock.tick(FPS)
