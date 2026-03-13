from machine import Pin, PWM
import time
import dht

# ---------- الإعدادات ----------
# ساعات الإغلاق (مثال: 22:00 - 06:00)
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

# دالة تحويل الزاوية للسيرفو
def set_servo_angle(servo, angle):
    duty = int((angle / 180 * 102) + 26)
    servo.duty(duty)

# دالة معرفة الوقت الحالي (نسبي، تجريبي)
def current_hour():
    # على Wokwi ممكن نغير الرقم يدوي للتجربة
    # مثال: hour = 23 يعني في وقت الإغلاق
    hour = 23
    return hour

while True:
    # ---------- 1. PIR + Buzzer خلال ساعات الإغلاق ----------
    hour = current_hour()
    if pir.value() == 1 and (hour >= CLOSING_HOUR_START or hour < CLOSING_HOUR_END):
        buzzer.value(1)
        print("PIR detected! Call Police!")
    else:
        buzzer.value(0)

    # ---------- 2. IR Sensor (صنبور الميه) ----------
    if ir_tap.value() == 1:
        set_servo_angle(servo_tap, 90)  # فتح الصنبور
    else:
        set_servo_angle(servo_tap, 0)   # غلق الصنبور

    # ---------- 3. DHT22 Fan ----------
    try:
        dht22.measure()
        temp = dht22.temperature()
        if temp >= FAN_TEMP_THRESHOLD:
            set_servo_angle(servo_fan, 90)
        else:
            set_servo_angle(servo_fan, 0)
    except:
        pass

    # ---------- 4. Smoke + DHT11 ----------
    try:
        dht11.measure()
        temp_fire = dht11.temperature()
        smoke_detected = mq2.value()
        if smoke_detected == 1 and temp_fire >= TEMP_FIRE_THRESHOLD:
            set_servo_angle(servo_rush, 90)  # رشاش الميه
            buzzer_rush.value(0)
        elif smoke_detected == 1:
            buzzer_rush.value(1)  # إنذار فقط
        else:
            set_servo_angle(servo_rush, 0)
            buzzer_rush.value(0)
    except:
        pass

    time.sleep(0.5)
