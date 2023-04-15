from machine import Pin, SoftI2C, PWM, RTC
import ssd1306, dht, machine, network, urequests, time

def set_color(r, g, b):
    red_pwm.duty(int(r / 255 * 1023))
    green_pwm.duty(int(g / 255 * 1023))
    blue_pwm.duty(int(b / 255 * 1023))

red_pwm, green_pwm, blue_pwm = [PWM(Pin(pin, Pin.OUT)) for pin in (15, 2, 4)]
i2c, sensorDHT, ldr = SoftI2C(scl=Pin(22), sda=Pin(21)), dht.DHT22(Pin(14)), Pin(23, Pin.IN)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
rtc = RTC()
rtc.datetime((2023, 2, 20, 1, 15, 53, 0, 0))
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('iPhone ของ Thanakar', '000000')

tempList, humList, pir_count = [], [], 0
api_key = "64BGIGIT97WKQXR4"

while not sta_if.isconnected():
    set_color(255, 0, 0); time.sleep(0.2); set_color(0, 255, 0); time.sleep(0.2); set_color(0, 0, 255); time.sleep(0.2)

while True:
    t = rtc.datetime()
    now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])
    set_color(0, 0, 255)
    sensorDHT.measure()
    temp, hum = sensorDHT.temperature(), sensorDHT.humidity()
    tempList.append(temp)
    humList.append(hum)

    if ldr.value() == 1:
        pir_count += 1
        round_left = 30 - (len(tempList) % 30)
        oled.fill(0)
        oled.text("Time: " + now, 2, 2)
        oled.text('-' * 128, 2, 10)
        oled.text(f"{round_left} left", 2, 20, 1)
        oled.text("Temp: " + str(temp) + " C", 2, 30, 1)
        oled.text("Humid: " + str(hum) + " %", 2, 40, 1)
        oled.text('-' * 128, 2, 50)
        oled.show()
    else:
        oled.fill(0)
        oled.show()

    if len(tempList) % 30 == 0:
        temp, hum, pir = sum(tempList) / len(tempList), sum(humList) / len(humList), pir_count
        tempList, humList, pir_count = [], [], 0
        url = f"https://api.thingspeak.com/update?api_key={api_key}&field1={temp}&field2={hum}&field3={pir}"
        status = urequests.get(url)
        
        if status.content.decode() != 0:
