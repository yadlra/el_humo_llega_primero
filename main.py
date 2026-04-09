# ============================================================
#  EL HUMO LLEGA PRIMERO — main.py
#  Air quality alarm for traditional wood-fire kitchens
#  Hardware: ESP32-C3 + SEN55 + WS2812B LED + Piezo buzzer
#  Author: tecnomilpa 
# ============================================================

import time
import machine
from machine import Pin, PWM, SoftI2C
import neopixel

# ── PIN DEFINITIONS ─────────────────────────────────────────
I2C_SDA    = 8      # SEN55 data
I2C_SCL    = 9      # SEN55 clock
LED_PIN    = 3      # WS2812B single LED
BUZZER_PIN = 4      # Piezo buzzer

# ── THRESHOLDS (µg/m³ for PM2.5) ────────────────────────────
# WHO guidelines: 15 µg/m³ 24h mean. Kitchen fire is intense.

THRESHOLD_WARN     = 35    # amber warning
THRESHOLD_DANGER   = 75    # red alarm — act now
THRESHOLD_CRITICAL = 150   # full alarm — leave room (OTHER POSSIBILITIES TO BE EXPLORED WITH FAMILY)

# ── SETUP ────────────────────────────────────────────────────

i2c    = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=100_000)
led    = neopixel.NeoPixel(Pin(LED_PIN), 1)
buzzer = PWM(Pin(BUZZER_PIN), freq=2000, duty=0)

# ── SEN55 I2C ADDRESS ────────────────────────────────────────

SEN55_ADDR = 0x69

# ── SEN55 COMMANDS ───────────────────────────────────────────

CMD_START_MEASUREMENT = b'\x00\x21'
CMD_READ_VALUES       = b'\x03\xC4'
CMD_STOP_MEASUREMENT  = b'\x01\x04'


def sen55_crc(data):
    """CRC-8 checksum for SEN55 data integrity."""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0x31 if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc


def sen55_start():
    """Tell SEN55 to begin measuring."""
    i2c.writeto(SEN55_ADDR, CMD_START_MEASUREMENT)
    time.sleep(1)  # sensor needs a moment to spin up


def sen55_read():
    """
    Read PM2.5, PM10, VOC, humidity, temperature from SEN55.
    Returns (pm25, pm10, voc, humidity, temp) or None on error.
    PM values in µg/m³ × 10 (divide by 10 for real value).
    """
    try:
        i2c.writeto(SEN55_ADDR, CMD_READ_VALUES)
        time.sleep_ms(20)
        raw = i2c.readfrom(SEN55_ADDR, 48)

        # Each value is 2 bytes + 1 CRC byte
        def extract(offset):
            d = raw[offset:offset+2]
            crc = raw[offset+2]
            if sen55_crc(d) != crc:
                raise ValueError("CRC mismatch")
            return (d[0] << 8 | d[1])

        pm10_raw  = extract(0)   # PM1.0
        pm25_raw  = extract(3)   # PM2.5  ← main alarm trigger
        pm40_raw  = extract(6)   # PM4.0
        pm100_raw = extract(9)   # PM10
        hum_raw   = extract(12)  # Humidity
        temp_raw  = extract(15)  # Temperature
        voc_raw   = extract(18)  # VOC index

        pm25 = pm25_raw / 10.0
        pm10 = pm100_raw / 10.0
        voc  = voc_raw / 10.0
        humidity = hum_raw / 100.0
        temp     = temp_raw / 200.0

        return pm25, pm10, voc, humidity, temp

    except Exception as e:
        print("Sensor read error:", e)
        return None


# ── LED COLOURS ──────────────────────────────────────────────

# Warm palette, instead of clinical something more fire adjacent (to be further explored)

COLOUR_OK       = (0, 40, 5)      # very dim warm green — breathing
COLOUR_WARN     = (80, 30, 0)     # amber glow
COLOUR_DANGER   = (120, 8, 0)     # deep red orange
COLOUR_CRITICAL = (180, 0, 0)     # full red pulse

def set_led(colour):
    led[0] = colour
    led.write()

def led_off():
    led[0] = (0, 0, 0)
    led.write()


# ── SOUND PATTERNS ───────────────────────────────────────────

# Tones that feel like a warning, not a machine error (to also be explored with family and others interested after first test)

def tone(freq, duration_ms, duty=512):
    buzzer.freq(freq)
    buzzer.duty(duty)
    time.sleep_ms(duration_ms)
    buzzer.duty(0)
    time.sleep_ms(30)

def sound_warn():
    """Two soft ascending tones — gentle nudge."""
    tone(880, 80, 300)
    tone(1100, 120, 300)

def sound_danger():
    """Three pulses — pay attention."""
    for _ in range(3):
        tone(1200, 100, 400)
        time.sleep_ms(80)

def sound_critical():
    """Urgent repeated alarm — leave the room."""
    for _ in range(6):
        tone(1500, 80, 600)
        time.sleep_ms(60)
        tone(900, 80, 500)
        time.sleep_ms(60)

def sound_breathe():
    """Single very soft tick every breathing cycle — alive signal."""
    tone(600, 30, 100)


# ── BREATHING ANIMATION (OK state) ───────────────────────────

# LED gently pulses like breathing — shows it's working (but may tweak if too confusing for people in the kitchen)

def breathe_once():
    """One slow breath — fade up, fade down."""
    r, g, b = COLOUR_OK
    steps = 20
    for i in range(steps):
        factor = i / steps
        led[0] = (int(r * factor), int(g * factor), int(b * factor))
        led.write()
        time.sleep_ms(40)
    for i in range(steps, 0, -1):
        factor = i / steps
        led[0] = (int(r * factor), int(g * factor), int(b * factor))
        led.write()
        time.sleep_ms(40)
    led_off()


# ── PULSE ANIMATION (alarm states) ───────────────────────────

def pulse_led(colour, times=3, speed_ms=150):
    r, g, b = colour
    for _ in range(times):
        for i in range(10):
            f = i / 10
            led[0] = (int(r*f), int(g*f), int(b*f))
            led.write()
            time.sleep_ms(speed_ms // 10)
        for i in range(10, 0, -1):
            f = i / 10
            led[0] = (int(r*f), int(g*f), int(b*f))
            led.write()
            time.sleep_ms(speed_ms // 10)


# ── MAIN LOOP ────────────────────────────────────────────────

def run():
    print("=" * 40)
    print("  EL HUMO LLEGA PRIMERO — starting up")
    print("  tecnomilpa ")
    print("=" * 40)

    sen55_start()
    print("Sensor warming up...")
    time.sleep(3)

    # Startup flash — system is alive
    set_led((20, 20, 20))
    time.sleep_ms(300)
    led_off()
    tone(700, 100, 200)

    last_alarm_time = 0
    alarm_cooldown  = 30_000  # ms — don't re-alarm too often

    while True:
        data = sen55_read()

        if data is None:
            # Sensor error — slow red blink
            print("Sensor error — check wiring")
            set_led((50, 0, 0))
            time.sleep_ms(500)
            led_off()
            time.sleep_ms(500)
            continue

        pm25, pm10, voc, humidity, temp = data
        now = time.ticks_ms()

        print(f"PM2.5: {pm25:.1f} µg/m³  |  PM10: {pm10:.1f}  |  VOC: {voc:.0f}  |  {temp:.1f}°C  {humidity:.0f}%RH")

        # ── Determine air quality level ──────────────────────
        if pm25 >= THRESHOLD_CRITICAL:
            level = "CRITICAL"
        elif pm25 >= THRESHOLD_DANGER:
            level = "DANGER"
        elif pm25 >= THRESHOLD_WARN:
            level = "WARN"
        else:
            level = "OK"

        print(f"  → Level: {level}")

        # ── React ────────────────────────────────────────────
        cooldown_elapsed = time.ticks_diff(now, last_alarm_time) > alarm_cooldown

        if level == "CRITICAL":
            pulse_led(COLOUR_CRITICAL, times=4, speed_ms=100)
            if cooldown_elapsed:
                sound_critical()
                last_alarm_time = time.ticks_ms()

        elif level == "DANGER":
            pulse_led(COLOUR_DANGER, times=3, speed_ms=180)
            if cooldown_elapsed:
                sound_danger()
                last_alarm_time = time.ticks_ms()

        elif level == "WARN":
            set_led(COLOUR_WARN)
            if cooldown_elapsed:
                sound_warn()
                last_alarm_time = time.ticks_ms()
            time.sleep_ms(2000)
            led_off()

        else:  # OK — breathe gently
            breathe_once()
            sound_breathe()

        # Read every 5 seconds
        time.sleep(5)


# ── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    run()
