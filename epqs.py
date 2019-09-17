import serial
import crccheck
from binascii import unhexlify
from binascii import hexlify
from bitarray import bitarray
import struct
import datetime

class EPQS:

    COM = {
        'ENQ': bytearray(b'\x01'),
        'DAT': bytearray(b'\x02'),
        'REC': bytearray(b'\x03'),
        'ECH': bytearray(b'\x04'),
        'AUT': bytearray(b'\x05'),
        'EOS': bytearray(b'\x06'),
        'DRJ': bytearray(b'\x0A'),
        'ARJ': bytearray(b'\x0B'),
    }
    dimensions = {
        '': bytearray(b'\x20'),
        'k': bytearray(b'\x6B'),
        'M': bytearray(b'\x4D'),
        'G': bytearray(b'\x47'),
    }

    debug = False

    def __init__(self, port, ADS, ADP, debug=False):
        self.serial_obj = serial.Serial(port=port)
        self.serial_obj.timeout = 0.5
        self.ADS = bytearray(ADS)
        self.ADP = bytearray(ADP)

        self.debug = debug

    def make_request(self, COM, DATA):
        N = bytearray(chr(len(DATA) + 11).encode())

        pack = {"N": N, "ADS": self.ADS, "ADP": self.ADP, "COM": bytearray(COM), "DATA": bytearray(DATA)}

        request = b""
        for i in pack.keys():
            request += pack[i]

        CRC = self.calc_crc16(request)[::-1]
        pack["CRC"] = bytearray(CRC)

        if self.debug:
            print('Final request: ' + pack)
        return pack

    def send_request(self, pack):
        for i in pack.keys():
            self.serial_obj.write(pack[i])
        return 0

    def get_response(self):
        n = self.serial_obj.read()
        if n:
            summ = n
            for i in range(ord(n) - 1):
                summ += self.serial_obj.read()
            return summ
        else:
            return False

    def pack_response(self, response):
        arr = bytearray(response)

        N = arr[0]
        arr = arr[1:]

        ADS = arr[:6]
        arr = arr[6:]

        ADP = arr[:1]
        arr = arr[1:]

        COM = arr[:1]
        arr = arr[1:]

        data_len = N-11
        DATA = arr[:data_len]
        arr = arr[data_len:]

        CRC = arr

        return {"N": N, "ADS": ADS, "ADP": ADP, "COM": COM, "DATA": DATA, "CRC": CRC}

    def check_request_crc(self, response):
        try:
            left = self.calc_crc16(bytearray(response[:-2]))
            right = bytearray(response)[-2:][::-1]
            return left == right
        except:
            return False

    def calc_crc16(self, hex_bytes):
        crc = crccheck.crc.CrcArc()
        res = crc.calc(hex_bytes)
        return unhexlify(hex(res)[2:])

    def get_load_profile(self):
        pass

    def decode_32bit_time(self, time_bytes):
        time_bits = bitarray()
        time_bytes = time_bytes[::-1]
        time_bits.frombytes(bytes(time_bytes))

        time = {
            "seconds": (int(time_bits[27:32].to01(), 2) * 2),
            "minutes": (int(time_bits[21:27].to01(), 2)),
            "hours": (int(time_bits[16:21].to01(), 2)),
            "day": (int(time_bits[11:16].to01(), 2)),
            "month": (int(time_bits[7:11].to01(), 2)),
            "year": (int(time_bits[0:7].to01(), 2))
            }
        return time


