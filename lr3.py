# Завантажено PyGame
import pygame
# Завантажено основний клас з бібліотеки для отримання функціоналу дрону.
from djitellopy import Tello

# Ініціалізовано дрон
drone = Tello()
drone.connect()
drone.takeoff()

# Ініціалізовано модулі PyGame
pygame.init()

# Отримано ширину екрану
screen = pygame.display.set_mode((1080, 720))

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
        # При закритті вікна зупиняємо головний цикл
        if event.type == pygame.QUIT: 
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