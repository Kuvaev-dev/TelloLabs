# Завантажено основний клас з бібліотеки для отримання функціоналу дрону.
from djitellopy import Tello
# Завантажено time для управління часом
import time 

# Створено об'єкт дрону
drone = Tello()

# Встановлено контакт між фізичним дроном та його об'єктом
drone.connect()

# Отримано відсоток заряду акумулятора
drone.get_battery()

# Отримано температуру дрону
drone.get_temperature()

# Отримано відстань до поверхні у сантиметрах
drone.get_distance_tof()

# Отримано висоту від рівня моря у сантиметрах
drone.get_barometer()

# Запущено дрон та піднято його над поверхнею
drone.takeoff()

# Переміщено дрон вперед на 50 сантиметрів
drone.move_forward(50)

# Переміщено дрон назад на 30 сантиметрів
drone.move_back(30)

# Обернено дрон за годинниковою стрілкою на 70 градусів
drone.rotate_clockwise(70)

# Піднято дрон вгору на 40 сантиметрів
drone.move_up(40)

# Переміщено дрон вперед на 50 сантиметрів за допомогою send_rc_control
drone.send_rc_control(0, 50, 0, 0)

# Зупинено час виконання на 2 секунди
time.sleep(2)

# Зупинено рон у повітрі
drone.send_rc_control(0, 0, 0, 0)

# Приземлено дрон на поверхню
drone.land()