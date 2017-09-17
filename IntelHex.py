#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Imports
import os.path
from MemoryBlock import MemoryBlock


class IntelHex:

    # Return values
    SUCCESS = 0
    FILE_NOT_FOUND = 1
    FILE_FORMAT_ERROR = 2
    MISSING_START_CODE = 3
    LINE_LENGTH_ERROR = 4
    CHECKSUM_ERROR = 5
    INVALID_RECORD_TYPE = 6

    # Record types
    DATA_RECORD = 0
    END_OF_FILE = 1
    EXT_SEG_ADDR = 2
    START_SEG_ADDR = 3
    EXT_LINEAR_ADDR = 4
    START_LINEAR_ADDR = 5

    # Misc. consts
    START_CODE_LEN = 1
    BYTE_COUNT_LEN = 2
    ADDRESS_LEN = 4
    RECORD_TYPE_LEN = 2
    CHECKSUM_LEN = 2
    EOL_LEN = 1
    FIXED_DATA_LEN = START_CODE_LEN + BYTE_COUNT_LEN + ADDRESS_LEN +    \
                     RECORD_TYPE_LEN + CHECKSUM_LEN + EOL_LEN
    DATA_START_POS = START_CODE_LEN + BYTE_COUNT_LEN + ADDRESS_LEN + RECORD_TYPE_LEN


    def __init__(self, fileName=''):
        # Private(ish) data
        self.__extendedAddress = 0
        self.__segmentAddress = 0
        self.__currentAbsoluteAddress = -1
        self.__eofRecordSeen = False


        # Public data
        self.fileName = fileName
        self.lineCount = 0
        self.blockList = []                 # Set of MemoryBlock instances (start address and data)


    def ParseLine(self, s):
        self.lineCount += 1

        # Check that nothing appears after the end-of-file record
        if self.__eofRecordSeen:
            return FILE_FORMAT_ERROR

        # Check start and end markers
        if s[0] != ':':
            return self.MISSING_START_CODE
        if s[-1] != '\n':
            return self.FILE_FORMAT_ERROR

        # Extract the non-data fields
        try:
            byteCount = int(s[1:3], 16)
            addrMsb = int(s[3:5], 16)
            addrLsb = int(s[5:7], 16)
            recordType = int(s[7:9], 16)
            checksum = int(s[-3:-1], 16)
        except:
            return self.FILE_FORMAT_ERROR

        # Check line length
        if (len(s) != self.FIXED_DATA_LEN + (2 * byteCount)):
            return self.LINE_LENGTH_ERROR

        # Extract any data, keeping a running checksum
        calculatedChecksum = byteCount + addrMsb + addrLsb + recordType + checksum
        dataPos = self.DATA_START_POS
        dataList = [None] * byteCount
        for n in range(0, byteCount):
            try:
                data = int(s[dataPos:dataPos + 2], 16)
            except:
                return self.FILE_FORMAT_ERROR
            calculatedChecksum += data
            dataPos += 2
            dataList[n] = data

        # Test the calculated checksum
        if ((calculatedChecksum & 0xFF) != 0):
            return self.CHECKSUM_ERROR

        # All looks OK so far, so process the record
        encodedAddress = (addrMsb << 8) + addrLsb
        if recordType == self.DATA_RECORD:
            # If the address is not contiguous, start a new memory block and add it to the block list
            newAbsoluteAddress = self.__extendedAddress + self.__segmentAddress + encodedAddress
            if newAbsoluteAddress != self.__currentAbsoluteAddress:
                self.__currentMemoryBlock = MemoryBlock(newAbsoluteAddress)
                self.blockList.append(self.__currentMemoryBlock)
            # Add the line data to the current (contiguous) memory block
            for d in dataList:
                self.__currentMemoryBlock.data.append(d)
            self.__currentAbsoluteAddress = newAbsoluteAddress + byteCount

        elif recordType == self.END_OF_FILE:
            if byteCount > 0:
                return self.FILE_FORMAT_ERROR
            self.__eofRecordSeen = True

        elif recordType == self.EXT_SEG_ADDR:
            if byteCount != 2:
                return self.FILE_FORMAT_ERROR
            self.__segmentAddress = (dataList[0] << 12) + (dataList[1] << 4)

        elif recordType == self.START_SEG_ADDR:
            if (encodedAddress != 0) or (byteCount != 4):
                return self.FILE_FORMAT_ERROR
            # Not sure what to do with this record type. Nothing, I think!!?

        elif recordType == self.EXT_LINEAR_ADDR:
            if byteCount != 2:
                return self.FILE_FORMAT_ERROR
            self.__extendedAddress = (dataList[0] << 24) + (dataList[1] << 16)

        elif recordType == self.START_LINEAR_ADDR:
            if (encodedAddress != 0) or (byteCount != 4):
                return self.FILE_FORMAT_ERROR
            # Not sure what to do with this record type. Nothing, I think!!?

        else:
            return self.INVALID_RECORD_TYPE
        return self.SUCCESS


    def Parse(self):
        if not os.path.exists(self.fileName):
            return self.FILE_NOT_FOUND
        self.__extendedAddress = 0
        self.__segmentAddress = 0
        self.__currentAbsoluteAddress = -1
        self.lineCount = 0
        self.__eofRecordSeen = False
        self.blockList = []
        with open(self.fileName,'r') as f:
            for line in f:
                lineResult = self.ParseLine(line)
                if lineResult != self.SUCCESS:
                    return lineResult
        if not self.__eofRecordSeen:
            return FILE_FORMAT_ERROR
        return self.SUCCESS
