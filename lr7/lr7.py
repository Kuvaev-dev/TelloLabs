import pygame
from djitellopy import Tello
import numpy as np 
import cv2 
from ultralytics import YOLO
import threading 

# Ініціалізація розмірів екрану та цільових координат для об'єкта
WIDTH = 640
HEIGHT = 480
TARGET_X = WIDTH / 2  # середина екрану
TARGET_Y = 120  # висота обрана на основі попереднього пролітання

# Ініціалізація Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 5
clock = pygame.time.Clock() 

# Ініціалізація моделі YOLO для розпізнавання об'єктів
model = YOLO("level-3/box-detector.pt")

# Ініціалізація дрона Tello
drone = Tello()
drone.connect()
drone.streamon()
frame_read = drone.get_frame_read()

# Ініціалізація змінних для керування рухом дрона
left_right_velocity = 0
forward_backward_velocity = 0
up_down_velocity = 0
yaw_velocity = 0

# Визначення режимів керування
GROUNDED = 0
MANUAL = 1
AUTOPILOT = 2
mode = GROUNDED

# Ініціалізація змінних для координат обмежувальної коробки та коефіцієнтів регулятора
box_x = 0
box_y = 0
Kp_x = -0.2
Kp_y = 0.3

# Основний цикл програми
while is_running: 
    # Обробка подій Pygame
    for event in pygame.event.get():
        # Обробка події закриття вікна
        if event.type == pygame.QUIT:
            if mode != GROUNDED: 
                threading.Thread(target=drone.land).start()
            drone.streamoff()
            is_running = False
        # Обробка клавіш
        if event.type == pygame.KEYDOWN:
            # Зміна режиму на GROUNDED
            if event.key == pygame.K_0 and mode != GROUNDED:
                threading.Thread(target=drone.land).start()
                mode = GROUNDED
            # Зміна режиму на MANUAL
            if event.key == pygame.K_1:
                if mode == GROUNDED:
                    threading.Thread(target=drone.takeoff).start()
                if mode == AUTOPILOT:
                    left_right_velocity = 0
                    forward_backward_velocity = 0
                    up_down_velocity = 0
                    yaw_velocity = 0
                mode = MANUAL
            # Зміна режиму на AUTOPILOT
            if event.key == pygame.K_2 and mode == MANUAL:
                mode = AUTOPILOT

        # Обробка подій для режиму MANUAL
        if mode == MANUAL:
            if event.type == pygame.KEYDOWN:
                # Наліво
                if event.key == pygame.K_LEFT:
                    left_right_velocity = -50
                # Направо
                if event.key == pygame.K_RIGHT:
                    left_right_velocity = 50
                # Вперед
                if event.key == pygame.K_UP:
                    forward_backward_velocity = 50
                # Назад
                if event.key == pygame.K_DOWN:
                    forward_backward_velocity = -50
                # Вгору
                if event.key == pygame.K_w:
                    up_down_velocity = 50
                # Вниз
                if event.key == pygame.K_s:
                    up_down_velocity = -50
                # Обертання проти годинникової стрілки
                if event.key == pygame.K_a:
                    yaw_velocity = -50
                # Обертання за годинниковою стрілкою
                if event.key == pygame.K_d:
                    yaw_velocity = 50
            # Обробка відпущених клавіш
            if event.type == pygame.KEYUP:
                left_right_velocity = 0 if event.key in [pygame.K_LEFT, pygame.K_RIGHT] else left_right_velocity
                forward_backward_velocity = 0 if event.key in [pygame.K_UP, pygame.K_DOWN] else forward_backward_velocity
                up_down_velocity = 0 if event.key in [pygame.K_w, pygame.K_s] else up_down_velocity
                yaw_velocity = 0 if event.key in [pygame.K_a, pygame.K_d] else yaw_velocity

    # Отримання та обробка кадру відео
    frame = frame_read.frame 
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # Прогнозування обмежувальних коробок за допомогою YOLO
    results = model.predict(frame, verbose=False)

    for bbox in results[0].boxes:
        xyxy = bbox.numpy().xyxy.astype(np.int_).flatten()
        # Розрахунок центру обмежувальної коробки 
        box_x = xyxy[0] + (xyxy[2] - xyxy[0]) / 2 
        box_y = xyxy[1] + (xyxy[3] - xyxy[1]) / 2
        # Малювання обмежувальної коробки на кадрі
        cv2.rectangle(
            frame,
            (xyxy[0], xyxy[1]),
            (xyxy[2], xyxy[3]),
            color=(0, 0, 255),
            thickness=2
        )

    # Конвертація та відображення кадру в Pygame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    frame = np.flipud(frame) 
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))

    # Режим AUTOPILOT: автоматичне керування дроном
    if mode == AUTOPILOT:
        if results[0].boxes:
            error_x = TARGET_X - box_x
            error_y = TARGET_Y - box_y
            
            left_right_velocity = int(Kp_x * error_x)
            forward_backward_velocity = 40
            up_down_velocity = int(Kp_y * error_y)
            yaw_velocity = 0
        else:
            left_right_velocity = 0
            forward_backward_velocity = 40
            up_down_velocity = 0
            yaw_velocity = 0

    # Надсилання команд управління до дрона
    if mode == MANUAL or mode == AUTOPILOT:
        drone.send_rc_control(
            left_right_velocity,
            forward_backward_velocity,
            up_down_velocity,
            yaw_velocity
        )
        
    pygame.display.flip() 
    clock.tick(FPS)
