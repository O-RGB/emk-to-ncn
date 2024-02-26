import zlib
import struct


class EMKDecoder:
    def __init__(self, emkFile, saveFolder):
        self.magic = True
        self.saveFolder = saveFolder
        self.encoding = False
        
        with open(emkFile, 'rb') as f:
            self.data = bytearray(f.read())

        xorKey = bytes.fromhex("AFF24C9CE9EA9943")
        for i in range(len(self.data)):
            self.data[i] ^= xorKey[i % len(xorKey)]

        magic = bytes.fromhex("2e53464453")
        if self.data[:len(magic)] != magic:
            self.magic = False
            print("Invalid magic test")

        headerPos = int.from_bytes(self.data[0x22:0x2a], 'little')
        headerEnd = int.from_bytes(self.data[0x2a:0x32], 'little')

        self.header = self.data[headerPos:headerEnd]

        self.off = 0

        self.sound_info = {}

        self.nameInfo = ""
        self.artistInfo = ""

        self.lyrics = ""
        self.midi = ""
        self.cursor = ""

    def getMagicError(self):
        return self.magic

    def skipBytes(self, n):
        self.off += n

    def readByte(self):
        v = self.header[self.off]
        self.off += 1
        return v

    def readUShort(self):
        v = struct.unpack('<H', self.header[self.off:self.off+2])[0]
        self.off += 2
        return v

    def readUInt(self):
        v = struct.unpack('<I', self.header[self.off:self.off+4])[0]
        self.off += 4
        return v

    def readString(self):
        len = self.readByte()
        str = self.header[self.off:self.off+len].decode('utf8')
        self.off += len
        return str

    def checkMagic(self, magic):
        data = self.header[self.off:self.off+len(magic)]
        if data != magic:
            raise ValueError("Invalid magic: " +
                             data.hex() + " != " + magic.hex())
        self.off += len(magic)

    def readTag(self):
        tag = self.readByte()
        if tag == 2:
            v = self.readByte()
            return v
        elif tag == 3:
            v = self.readUShort()
            return v
        elif tag == 4:
            v = self.readUInt()
            return v
        elif tag == 6:
            v = self.readString()
            return v
        else:
            raise ValueError("Unknown tag: 0x" + format(tag, 'x'))
        
    def setEncodeText(self):
        self.encoding = True

    def decodeEmk(self):
        try:
            magic = bytes.fromhex("53464453")  # SFDS
            while self.off < len(self.header):
                self.checkMagic(magic)
                tag = self.readTag()
                uncompressedSize = self.readTag()
                unk2 = self.readTag()
                dataBegin = self.readTag()
                dataEnd = self.readTag()
                unk5 = self.readTag()
                unk6 = self.readTag()
                self.skipBytes(0x10)
                unk7 = self.readTag()
                unk8 = self.readTag()

                compressedData = self.data[dataBegin:dataEnd]
                rawData = zlib.decompress(compressedData)
                if len(rawData) != uncompressedSize:
                    raise ValueError("Invalid uncompressed size")
                ext = {
                    "HEADER": "txt",
                    "MIDI_DATA": "mid",
                    "LYRIC_DATA": "txt",
                    "CURSOR_DATA": "bin",
                    "SONG_INFO": "bin",
                }
                filename = tag + "." + (ext.get(tag, "bin"))

                mode = 'wb'
                if self.encoding and tag not in ["MIDI_DATA", "CURSOR_DATA"]:
                    mode = 'w'
                    rawData = rawData.decode("cp874")

                with open("/".join([self.saveFolder, filename]), mode) as f:
                    f.write(rawData)

            return True
        except Exception as e:
            print(e)
            return False

    def getSoundInfo(self):
        return self.nameInfo, self.artistInfo

    def getBase64Data(self):
        return {
            "lyr": self.lyrics,
            "cur": self.cursor,
            "mid": self.midi
        }
