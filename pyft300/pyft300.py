"""
Filename: pyft300.py
Author: Eytan Canzini
Date: 24-02-2026
License: CC-BY-4.0
"""
import serial
import numpy as np
import minimalmodbus as mm
import libscrc

BAUDRATE = 19200
BYTESIZE = 8
PARITY = "N"
STOPBITS = 1
TIMEOUT = 1
SLAVEADDRS = 9
REGISTER = 410
INITIAL_VAL = 0x0200

class Sensor:
    """
    This is a minimal working example for the Robotiq Force Torque 300 sensor to be used on a generic robot arm using serial and MODBUS communication. The code is designed for prototypging and to be "hackable", so don't expect production-level comments.
    """
    def __init__(self, port):
        
        # Misc variables
        self.num_samples_zero = 100

        # Initialise the serial connection
        self.ser = serial.Serial(
            port=port,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=TIMEOUT
        )

        # Initialise minimal MODBUS
        mm.BAUDRATE=BAUDRATE
        mm.BYTESIZE=BYTESIZE
        mm.PARITY=PARITY
        mm.STOPBITS=STOPBITS
        mm.TIMEOUT=TIMEOUT

        # Initialise MODBUS interface for the sensor
        self.ft300 = mm.Instrument(
            port=port,
            slaveaddress=SLAVEADDRS
        )
        self.ft300.close_port_after_each_call = True
        self.ft300.mode = mm.MODE_RTU
        _ = self.ft300.write_register(
            registeraddress=REGISTER,
            value=INITIAL_VAL
        )

        # Initialise the serial connection and initialise streaming
        self.start_bytes = bytes([0x20, 0x4E])
        _ = self.ser.read_until(self.start_bytes) # This message is normally unread by the sensor, but is used to ensure no dropped frames
        self.mean_reading = self.zero_sensor

    @property
    def read_sensor(self) -> np.ndarray:
        """
        Reads the sensor value and returns a vector of forces and torques

        Returns:
            np.ndarray: Numpy 6x1 vector of the forces and torques (normalised)
        """
        return self._get_force_torque()
    
    @property
    def zero_sensor(self) -> np.ndarray:
        """
        Zeroes the sensor based on 100 samples (can be tuned)

        Returns:
            np.ndarray: Average (mean) vector for the number of samples
        """
        temp = np.zeros((6,1))
        for _ in range(1,(self.num_samples_zero+1)):
            temp += self._get_raw_ft()
        return temp/self.num_samples_zero
    
    def close(self) -> None:
        """
        Closes the serial connection (used when finishing an application).
        """
        packet = bytearray()
        send_count = 0
        while send_count < 50:
            packet.append(0xFF)
            send_count += 1
        self.ser.write(packet)
        self.ser.close()

    def _get_force_torque(self) -> np.ndarray:
        return np.round((self._get_raw_ft() - self.mean_reading), decimals=2)

    def _get_raw_ft(self) -> np.ndarray:
        """
        Reads the raw sensor values from the serial interface

        Raises:
            Exception: If the CRC and serial message don't match, an exception is thrown

        Returns:
            np.ndarray: Numpy 6x1 vector of the raw forces and torquesr
        """
        data = self.ser.read_until(self.start_bytes)
        data_arr = bytearray(data)
        data_arr = self.start_bytes+data_arr[:-2]
        if self._crc_check(data_arr) is False:
            raise Exception("CRC ERROR: Serial message and CRC does not match")
        return self._ft_from_serial_msg(data_arr)


    def _crc_check(self, serial_msg) -> bool:
        """
        Check if the serial message has a valid CRC.

        Args:
            serial_msg:  Serial message

        Returns:
            check_result (bool): Boolean returning the outcome of the CRC check
        """
        #CRC from serial message
        crc = int.from_bytes(serial_msg[14:16], byteorder='little', signed=False)
        #calculated CRC
        crc_calc = libscrc.modbus(serial_msg[0:14])
        
        if crc == crc_calc:
            check_result = True
        else:
            check_result = False
        return check_result
    
    def _ft_from_serial_msg(self, msg) -> np.ndarray:
        """
        Convert the serial message in bytes into the numpy vector for the force and torque values.

        Args:
            msg (bytearray): Array of bytes of the serial message

        Returns:
            _ (np.ndarray): 6x1 vector of the raw force and torque measurements
        """
        return np.array([
            [int.from_bytes(msg[2:4], byteorder="little", signed=True)/100],
            [int.from_bytes(msg[4:6], byteorder="little", signed=True)/100],
            [int.from_bytes(msg[6:8], byteorder="little", signed=True)/100],
            [int.from_bytes(msg[8:10], byteorder="little", signed=True)/1000],
            [int.from_bytes(msg[10:12], byteorder="little", signed=True)/1000],
            [int.from_bytes(msg[12:14], byteorder="little", signed=True)/1000]
        ])
        
