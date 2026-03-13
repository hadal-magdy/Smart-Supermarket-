from machine import Pin, PWM, time_pulse_us
import time
import dht

# ---------- الإعدادات ----------
CLOSING_HOUR_START = 22
CLOSING_HOUR_END = 6

# PIR + Buzzer
pir = Pin(14, Pin.IN)
buzzer = Pin(27, Pin.OUT)

# IR Sensor + Servo (Water Tap)
ir_tap = Pin(32, Pin.IN)
servo_tap = PWM(Pin(26), freq=50)

# DHT22 + Servo (Fan)
dht22 = dht.DHT22(Pin(33))
servo_fan = PWM(Pin(25), freq=50)
FAN_TEMP_THRESHOLD = 30

# Smoke + DHT11 + Servo (Water Rush) + Buzzer
mq2 = Pin(12, Pin.IN)
dht11 = dht.DHT11(Pin(34))
servo_rush = PWM(Pin(23), freq=50)
buzzer_rush = Pin(27, Pin.OUT)
TEMP_FIRE_THRESHOLD = 40

# ✅ الباب: Ultrasonic HC-SR04 + Servo
trig = Pin(5, Pin.OUT)
echo = Pin(19, Pin.IN)
servo_door = PWM(Pin(18), freq=50)
DOOR_DISTANCE_CM = 20  # لو حد أقرب من 20cm → افتح الباب

def set_servo_angle(servo, angle):
    duty = int((angle / 180 * 102) + 26)
    servo.duty(duty)

def get_distance_cm():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    try:
        duration = time_pulse_us(echo, 1, 30000)
        distance = (duration / 2) / 29.1
        return distance
    except:
        return 999  # مفيش حاجة قدام

def current_hour():
    hour = 10  # غيّر للتجربة: 10 = وقت عمل، 23 = إغلاق
    return hour

def is_closing_time(hour):
    return hour >= CLOSING_HOUR_START or hour < CLOSING_HOUR_END

# الباب مقفول في البداية
set_servo_angle(servo_door, 0)

while True:
    hour = current_hour()

    # ---------- 1. PIR + Buzzer ----------
    if pir.value() == 1 and is_closing_time(hour):
        buzzer.value(1)
        print("PIR detected! Call Police!")
    else:
        buzzer.value(0)

    # ---------- 2. الباب (Ultrasonic) ----------
    distance = get_distance_cm()
    if not is_closing_time(hour):
        if distance < DOOR_DISTANCE_CM:
            set_servo_angle(servo_door, 90)  # فتح الباب
            print(f"الباب مفتوح - المسافة: {distance:.1f} cm")
        else:
            set_servo_angle(servo_door, 0)   # غلق الباب
            print(f"الباب مقفول - المسافة: {distance:.1f} cm")
    else:
        set_servo_angle(servo_door, 0)  # مقفول دايماً وقت الإغلاق
        print("وقت إغلاق - الباب مقفول")

    # ---------- 3. IR Sensor (صنبور الميه) ----------
    if ir_tap.value() == 1:
        set_servo_angle(servo_tap, 90)
    else:
        set_servo_angle(servo_tap, 0)

    # ---------- 4. DHT22 Fan ----------
    try:
        dht22.measure()
        temp = dht22.temperature()
        if temp >= FAN_TEMP_THRESHOLD:
            set_servo_angle(servo_fan, 90)
        else:
            set_servo_angle(servo_fan, 0)
    except:
        pass

    # ---------- 5. Smoke + DHT11 ----------
    try:
        dht11.measure()
        temp_fire = dht11.temperature()
        smoke_detected = mq2.value()
        if smoke_detected == 1 and temp_fire >= TEMP_FIRE_THRESHOLD:
            set_servo_angle(servo_rush, 90)
            buzzer_rush.value(0)
        elif smoke_detected == 1:
            buzzer_rush.value(1)
        else:
            set_servo_angle(servo_rush, 0)
            buzzer_rush.value(0)
    except:
        pass

    time.sleep(0.5)
