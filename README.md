# DFUGen
Generate a Device Firmware Upgrade (DFU) file from an Intel hex file.

Simple usage:
```
python DFUGen.py file1.hex [file2.hex [filen.hex]] -o filename.dfu
```
For all options:
```
python DFUGen.py --help
```
Not much testing has been done with multiple input (hex) files.
