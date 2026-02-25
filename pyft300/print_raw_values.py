from pyft300 import Sensor
import time

# Depending on whether you are using Linux or Windows, the sensor will either be a /dev/ttyUSB device or a COM device. 
PORTNAME = "/dev/ttyUSB0"

if __name__ == "__main__":
    
    try: 
        # A try-finally loop is needed when using the sensor to ensure that the sensor closes itself once the application ends or is terminated. 

        ft = Sensor(port=PORTNAME)

        start_time = time.time()
        num_messages = 0
        frequency = 0

        print(f"Connection established on {PORTNAME}")

        while True:
            vals = ft.read_sensor

            num_messages += 1
            elapsed_time = time.time() - start_time
            freq = round(num_messages/elapsed_time)

            print(f"Sample Freq: {freq} Hz, FT Vals: {vals.T}")

    finally:
        ft.close()

