import time
import csv
from datetime import datetime
from sensirion_i2c_driver import I2cConnection, LinuxI2cTransceiver
from sensirion_i2c_sen5x import Sen5xI2cDevice

csv_path = "/home/raspberrypi_q/air_quality.csv"

with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
    device = Sen5xI2cDevice(I2cConnection(i2c_transceiver))
    device.device_reset()
    device.start_measurement()
    print("Logging to", csv_path, "- press Ctrl+C to stop")

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["timestamp", "pm1p0", "pm2p5", "pm4p0",
                             "pm10p0", "humidity", "temperature",
                             "voc_index", "nox_index"])

        while True:
            while device.read_data_ready() is False:
                time.sleep(0.1)
            v = device.read_measured_values()
            row = [
                datetime.now().isoformat(timespec="seconds"),
                v.mass_concentration_1p0.physical,
                v.mass_concentration_2p5.physical,
                v.mass_concentration_4p0.physical,
                v.mass_concentration_10p0.physical,
                v.ambient_humidity.percent_rh,
                v.ambient_temperature.degrees_celsius,
                v.voc_index.scaled,
                v.nox_index.scaled,
            ]
            writer.writerow(row)
            f.flush()
            print(f"{row[0]}  PM2.5={row[2]:.1f}  PM10={row[4]:.1f}  VOC={row[7]}")