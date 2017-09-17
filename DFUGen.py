#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# DFU (Device Firmware Upgrade) file generator for use with the STMicroelectronics DfuSe Demo application (V3.0.5).
# Reference document UM0391, User Manual, DfuSe File Format Specification, Rev 1, June 2007.

# Imports
from IntelHex import IntelHex
from DFUPrefix import DFUPrefix
from TargetPrefix import TargetPrefix
from DFUSuffix import DFUSuffix
import argparse
import binascii

# Functions
def main():
    # Define, extract and validate (where possible) the command-line arguments
    parser = argparse.ArgumentParser(description='Generate a DFU file from Intel hex file(s).')
    parser.add_argument('HexFile', nargs='+', help='List of input files')
    parser.add_argument('--version', action='version', version='DFUGen V1.0')
    parser.add_argument('-q', action="store_true", dest='quiet', default=False, help='Quiet. Do not show progress output')
    parser.add_argument('-d', metavar='<device-id>', dest='deviceID', action="store", default='ffff', help='Device ID (hex), default=FFFF')
    parser.add_argument('-p', metavar='<product-id>', dest='productID', action="store", default='ffff', help='Product ID (hex), default=FFFF')
    parser.add_argument('-v', metavar='<vendor-id>', dest='vendorID', action="store", default='ffff', help='Vendor ID (hex), default=FFFF')
    parser.add_argument('-i', metavar='<image name>', dest='imageName', default='', help='Only applies for first file in the list')
    parser.add_argument('-o', metavar='<file>', dest='outFile', action='store', required=True, help='Put the output into <file>')
    args = parser.parse_args()
    hexFiles = args.HexFile
    try:
        deviceId = int(args.deviceID, 16)
    except:
        print 'Invalid device ID'
        return
    try:
        productId = int(args.productID, 16)
    except:
        print 'Invalid product ID'
        return
    try:
        vendorId = int(args.vendorID, 16)
    except:
        print 'Invalid vendor ID'
        return

    # Iterate through each image (hex file)
    imageCount = 0
    success = True
    outputFileData = []
    fileCount = 0
    for hexFile in hexFiles:
        fileCount += 1
        hf = IntelHex(hexFile);
        parseResult = hf.Parse()
        if parseResult == IntelHex.SUCCESS:
            if not args.quiet:
                print "Successfully parsed %d lines of '%s'" %(hf.lineCount, hf.fileName)
            imageCount += 1

            # Iterate through each element (memory block) in the image and make a single element list
            elementList = []
            totalElementLength = 0
            for element in hf.blockList:
                elementSize = len(element.data)
                if not args.quiet:
                    print 'Address: {0:08X}, Length: {1:08X}'.format(element.startAddress, elementSize)
                # Each image element (contiguous memory block) is made up of the start address, length and data
                imageElement = [
                    (element.startAddress >> 0x00) & 0xFF,
                    (element.startAddress >> 0x08) & 0xFF,
                    (element.startAddress >> 0x10) & 0xFF,
                    (element.startAddress >> 0x18) & 0xFF,
                    (elementSize >> 0x00) & 0xFF,
                    (elementSize >> 0x08) & 0xFF,
                    (elementSize >> 0x10) & 0xFF,
                    (elementSize >> 0x18) & 0xFF
                ]
                imageElement += element.data
                # The element list is a single list of contiguous data. So add, don't append
                elementList += imageElement
                totalElementLength += len(imageElement)

            # Generate a target prefix for the current image (hex file)
            if (fileCount == 1) and (len(args.imageName) > 0):
                imageName = args.imageName
            else:
                imageName = hexFile
            targetPrefix = TargetPrefix(imageName, totalElementLength, len(hf.blockList)).data

            # Add the target prefix and all elements to the output data
            outputFileData += targetPrefix + elementList
        else:
            if not args.quiet:
                print 'Error %d found on line %d' %(parseResult, hf.lineCount)
            success = False
            break


    if success:
        # ToDo: How about testing that there are no overlapping memory segments?

        # The DFU Prefix can be generated now the image size is known
        dfuPrefixBlock = DFUPrefix(len(outputFileData), imageCount).data
        dfuPrefixByteArray = bytearray(dfuPrefixBlock)

        # Generate the CRC and the DFU Suffix block
        crc =  binascii.crc32(dfuPrefixByteArray)
        outputFileDataByteArray = bytearray(outputFileData)
        crc =  binascii.crc32(outputFileDataByteArray, crc)

        dfuSuffixBlock = DFUSuffix()
        dfuSuffixBlock.GenerateNoCrc(deviceId, productId, vendorId)
        crc = binascii.crc32(bytearray(dfuSuffixBlock.data), crc)
        # The python CRC calculation is different from that used by the DFU file manager.
        # A final XOR / inversion is required
        crc ^= 0xFFFFFFFF
        dfuSuffixBlock.AppendCrc(crc)
        dfuSuffixByteArray = bytearray(dfuSuffixBlock.data)

        # Write all the data to the output file
        try:
            with open(args.outFile,'wb') as f:
                f.write(dfuPrefixByteArray)
                f.write(outputFileDataByteArray)
                f.write(dfuSuffixByteArray)
        except:
            print 'Unable to open output file %s' %args.outFile


# Program entry point
if __name__ == "__main__":
    main()