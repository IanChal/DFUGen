#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class MemoryBlock:
    """Defines a single, contiguous memory block, with a start address and data"""

    def __init__(self, startAddress = -1):
        self.startAddress = startAddress
        self.data = []
