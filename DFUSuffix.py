#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class DFUSuffix(object):
    """Generates the DFU suffix block"""

    DFU_SUFFIX_LENGTH = 16
    DFU_SPEC_NUMBER_LSB = 0x1A
    DFU_SPEC_NUMBER_MSB = 0x01

    def GenerateNoCrc(self, deviceID=0xFFFF, ProductID=0xFFFF, VendorID=0xFFFF):
        self.data = [
            # Spec calls this 'Device field', the DFU FIle Manager calls it 'Version'
            (deviceID >> 0x00) & 0xFF,
            (deviceID >> 0x08) & 0xFF,
            (ProductID >> 0x00) & 0xFF,
            (ProductID >> 0x08) & 0xFF,
            (VendorID >> 0x00) & 0xFF,
            (VendorID >> 0x08) & 0xFF,
            self.DFU_SPEC_NUMBER_LSB,
            self.DFU_SPEC_NUMBER_MSB,
            ord('U'),
            ord('F'),
            ord('D'),
            self.DFU_SUFFIX_LENGTH,
        ]

    def AppendCrc(self, crc):
        self.data.append((crc >> 0x00) & 0xFF)
        self.data.append((crc >> 0x08) & 0xFF)
        self.data.append((crc >> 0x10) & 0xFF)
        self.data.append((crc >> 0x18) & 0xFF)
