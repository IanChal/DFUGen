class TargetPrefix:
    """Generates the target prefix block"""

    TARGET_PREFIX_LENGTH = 274
    MAX_TARGET_NAME_LEN = 255
    TARGET_NAME_POS = 11

    def __init__(self, targetName = '', targetSize = 0, elementCount = 0):
        self.data = [0] * self.TARGET_PREFIX_LENGTH
        self.data[0] = ord('T')             # Bytes 0-5 are the target signature
        self.data[1] = ord('a')
        self.data[2] = ord('r')
        self.data[3] = ord('g')
        self.data[4] = ord('e')
        self.data[5] = ord('t')
        self.data[6] = 0x00                 # Bool. Alternate setting. I don't know what this means.
        self.data[7] = 0x01                 # Bool. Target is named.
        self.data[8] = 0x00
        self.data[9] = 0x00
        self.data[10] = 0x00

        # Insert the target name in bytes 11-265
        size = min(self.MAX_TARGET_NAME_LEN, len(targetName))
        c = 0
        for n in range (self.TARGET_NAME_POS, self.TARGET_NAME_POS + size):
            self.data[n] = ord(targetName[c])
            c += 1
        # DFU File manager (V3.0.5) appears to pad the TargetName field with nonsense, but the string terminator
        # is present so it doesn't matter. I'm not going to do this, as it looks like an error to me.

        # Insert the size & number of elements in bytes 266-273
        self.data[266] = (targetSize >> 0x00) & 0xFF
        self.data[267] = (targetSize >> 0x08) & 0xFF
        self.data[268] = (targetSize >> 0x10) & 0xFF
        self.data[269] = (targetSize >> 0x18) & 0xFF
        self.data[270] = (elementCount >> 0x00) & 0xFF
        self.data[271] = (elementCount >> 0x08) & 0xFF
        self.data[272] = (elementCount >> 0x10) & 0xFF
        self.data[273] = (elementCount >> 0x18) & 0xFF
