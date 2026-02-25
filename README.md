# `pyFT300` - A Python Force-Torque Sensing Package

A minimal driver for the Robotiq FT-300 sensor using serial and Modbus communication.

## Dependencies

The package contains an `environment.yaml` file to replicate the Anaconda environment used during testing. However, the easiest way is to create your own environment. The package relies only on a few external packages:

- `libscrc`
- `minimalmodbus`
- `numpy`
- `pyserial`

To install all of these, run the following command in your virtual environment:

```bash
pip install libscrc minimalmodbus numpy pyserial
```

## Usage

The repository contains two files. The first, `print_raw_values.py` is a simple Python script that uses the package to read the raw (zeroed) values from the sensor. It is an example of how you would build the package into your application using the 100Hz sample rate of the sensor. The second, `pyft300.py`, is the class file that encompasses the main functions. It is commented to explain what each function does. 
