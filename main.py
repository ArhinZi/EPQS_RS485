import epqs
import time
from bitarray import bitarray

def request(epqs):
    response_pack = []
    is_fail_response = False
    for i in range(10):
        request_pack = epqs.make_request(COM=epqs.COM['ENQ'], DATA=b'\x18\x00\x00')
        # print("Sending {0}".format(request_pack))
        epqs.send_request(request_pack)
        response = epqs.get_response()
        if not response:
            is_fail_response = False
            # print("Response not found. Repeat request.")
            continue
        else:
            if not epqs.check_request_crc(response):
                is_fail_response = True
                # print("Bad connection. Repeat request.")
                continue
            else:
                is_fail_response = False
                response_pack = epqs.pack_response(response)
                print("Response {0}".format(response_pack))
                time_bits = bitarray()
                time_bits.frombytes(bytes(response_pack["DATA"][:4]))
                return (epqs.decode_32bit_time(response_pack["DATA"][:4]), time_bits, time_bits[0:16], time_bits[16:32], response_pack["DATA"][:4])
                break
    if is_fail_response:
        print("Bad connection. Terminated.")

    return 0



if __name__ == "__main__":
    epqs = epqs.EPQS(port='COM3', ADS=b"\x99\x68\x20\x02\x00\x00", ADP=b'\x01')

    for i in range(1):
        print(request(epqs))
        time.sleep(5)
