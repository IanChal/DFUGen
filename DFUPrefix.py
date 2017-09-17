#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class DFUPrefix:
    """Generates the DFU prefix block"""

    DFU_PREFIX_LENGTH = 11
    DFU_PREFIX_SIZE_POS = 6
    DFU_PREFIX_IMG_COUNT_POS = 10

    def __init__(self, imageSize = 0, targetCount = 0):
        # It looks like the DFU image size includes the DFU Prefix block but excludes the DFU Suffix block
        if imageSize != 0:
            imageSize += self.DFU_PREFIX_LENGTH
        self.data = [
                ord("D"),                   # Bytes 0-4 are the file signature
                ord('f'),
                ord('u'),
                ord('S'),
                ord('e'),
                0x01,                       # Version number (currently always 1)
                (imageSize >> 0x00) & 0xFF,
                (imageSize >> 0x08) & 0xFF,
                (imageSize >> 0x10) & 0xFF,
                (imageSize >> 0x18) & 0xFF,
                targetCount
        ]
