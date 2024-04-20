# Завантажено PyGame
import pygame
# Завантажено основний клас з бібліотеки для отримання функціоналу дрону.
from djitellopy import Tello
# Завантажено NumPy та OpenCV для виправлення зображення з дрону
import numpy as np
import cv2

# Ініціалізовано дрон
drone = Tello()
drone.connect()
drone.takeoff()

# Ініціалізація стріму з камери дрону
drone.streamon()

# Ініціалізовано модулі PyGame
pygame.init()

# Отримано ширину екрану
screen = pygame.display.set_mode((1080, 720))
# Створено змінні часу та кількості кадрів в секунду
clock = pygame.time.Clock()
FPS = 30
# Задання шрифту відображення показників
font = pygame.font.SysFont("presstart2p", size = 20)

# Отримано поточний кадр з камери дрону
frameRead = drone.get_frame_read()

# Створено головний цикл застосунку
isFlying = True

# Рух ліворуч - праворуч
leftRightVelocity = 0
# Рух вперед - назад
forwardBackwardVelocity = 0
# Рух вгору - вниз
upDownVelocity = 0
# Розворот
yawVelocity = 0

# Створено головний цикл для роботи вікна
while isFlying:
    # Створено вкладений цикл для проходження по подіях ітерації головного циклу
    for event in pygame.event.get():
        # При закритті вікна зупиняємо головний цикл / зупиняємо стрімінг з камери
        if event.type == pygame.QUIT: 
            drone.streamoff()
            drone.land()
            isFlying = False

        # Зміна швидкості дрону при натисканні клавіш напрямку
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                #print("Швидкість: 100")
                leftRightVelocity = 50
            if event.key == pygame.K_RIGHT:
                leftRightVelocity = -50
            if event.key == pygame.K_UP:
                forwardBackwardVelocity = 50
            if event.key == pygame.K_DOWN:
                forwardBackwardVelocity = -50
            if event.key == pygame.K_w:
                upDownVelocity = 50
            if event.key == pygame.K_s:
                upDownVelocity = -50
            if event.key == pygame.K_a:
                yawVelocity = 50
            if event.key == pygame.K_d:
                yawVelocity = -50

        # Зміна швидкості назад на 0 при відпусканні клавіш напрямку
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                #print("Швидкість: 0")
                leftRightVelocity = 0
            if event.key == pygame.K_RIGHT:
                leftRightVelocity = 0
            if event.key == pygame.K_UP:
                forwardBackwardVelocity = 0
            if event.key == pygame.K_DOWN:
                forwardBackwardVelocity = 0
            if event.key == pygame.K_w:
                upDownVelocity = 0
            if event.key == pygame.K_s:
                upDownVelocity = 0
            if event.key == pygame.K_a:
                yawVelocity = 0
            if event.key == pygame.K_d:
                yawVelocity = 0
    
    # Встановлення швидкості для дрона
    drone.send_rc_control(leftRightVelocity, forwardBackwardVelocity, upDownVelocity, yawVelocity)
    
    # Передача поточного кадру PyGame та оновлення дісплею
    frame = frameRead.frame
    # Зміна кольорової моделі на RGB для кореткного відображення кольорів
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    frame = np.flipud(frame)
    # Стабілізація зображення
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))
    # Виведення показників заряду батареї, TOF та температури дрону на екран
    screen.blit(
        font.render("Заряд батареї: " + str(drone.get_battery()) + "%", True, (164, 251, 147), (15, 690))
    )
    screen.blit(
        font.render("TOF: " + str(drone.get_distance_tof()) + " см", True, (164, 251, 147), (325, 690))
    )
    screen.blit(
        font.render("Температура: " + str(drone.get_temperature()) + " С", True, (164, 251, 147), (645, 690))
    )
    pygame.display.flip()
    # Вставновлення швидкості кадрів для фрейму
    clock.tick(FPS)