import socket
from crc_input import calcrc, verify_packet
#a1031e000000000000000000000036000002100002ffff00000000f00103c500005469

# ── Response payload (without CRC — server will append it) ──────────────────
# a1 03 1e 00 00 00 00 00 00 00 00 00 00 00 36 00 00 02 10 00 02 ff ff 00 00 00 00 f0 01 03 c5 00 00 54 69
RESPONSE_DATA = bytes.fromhex(
    'a1031e000000000000000000000036000002100002ffff00000000f00103c500005469'
)

########### NEXT STEP ##############
###Also Calculate the CRC for the main data and verify to the client side before displaying...

def parse_response(data: bytes):
    """
    Buffer indexing (1-based as per your spec):
    Buf[17] = data[16]  → Alarm 1–8  (byte index 16)
    Buf[18] = data[17]  → Alarm 1–8  (byte index 17)

    Word registers (1-based pairs → 0-based):
    HC_con  → Buf[7,8]   = data[6:8]
    AS_con  → Buf[9,10]  = data[8:10]
    CM_con  → Buf[11,12] = data[10:12]
    CP_con  → Buf[13,14] = data[12:14]
    CS_con  → Buf[15,16] = data[14:16]
    """
    print("\n─── Parsed Response ───────────────────────────────────")
    print(f"  Full packet ({len(data)} bytes): {data.hex(' ').upper()}")

    if len(data) < 18:
        print("  ⚠️  Packet too short to parse all fields.")
        return

    buf17 = data[16]
    buf18 = data[17]
    print(f"\n  Buffer[17] Alarm 1–8 : 0x{buf17:02X}  ({buf17:08b}b)")
    print(f"  Buffer[18] Alarm 1–8 : 0x{buf18:02X}  ({buf18:08b}b)")

    def word(hi, lo):
        return (hi << 8) | lo

    hc  = word(data[6],  data[7])
    as_ = word(data[8],  data[9])
    cm  = word(data[10], data[11])
    cp  = word(data[12], data[13])
    cs  = word(data[14], data[15])

    print(f"\n  HC_con [7,8]   : 0x{hc:04X}  ({hc})")
    print(f"  AS_con [9,10]  : 0x{as_:04X}  ({as_})")
    print(f"  CM_con [11,12] : 0x{cm:04X}  ({cm})")
    print(f"  CP_con [13,14] : 0x{cp:04X}  ({cp})")
    print(f"  CS_con [15,16] : 0x{cs:04X}  ({cs})")
    print("────────────────────────────────────────────────────────\n")


HOST, PORT = '127.0.0.1', 12345

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on {HOST}:{PORT} ...")

    client_socket, address = server_socket.accept()
    print(f"Connected to client: {address}\n")

    while True:
        raw = client_socket.recv(1024)
        if not raw:
            print("Client disconnected.")
            break

        print(f"Received ({len(raw)} bytes): {raw.hex(' ').upper()}")

        # ── CRC verification ─────────────────────────────────────────────────
        if len(raw) >= 3:                      # need at least data + 2 CRC bytes
            crch, crcl, valid = verify_packet(raw)
            if valid:
                print(f"✅ CRC OK  (CRCH={crch:02X}, CRCL={crcl:02X})")
            else:
                print(f"❌ CRC MISMATCH! Calculated CRCH={crch:02X} CRCL={crcl:02X}")
        else:
            print("⚠️  Packet too short for CRC check.")

        # ── Send response ─────────────────────────────────────────────────────
        # Append fresh CRC to the response data before sending
        data_only   = RESPONSE_DATA        # 34 bytes (no CRC yet)
        data_list   = list(data_only)
        ldata       = len(data_list) - 1
        resp_crch, resp_crcl = calcrc(data_list, ldata)
        response_packet = data_only + bytes([resp_crch, resp_crcl])

        print(f"\nSending response ({len(response_packet)} bytes): "
              f"{response_packet.hex(' ').upper()}")
        print(f"  → Appended CRC: CRCH={resp_crch:02X}  CRCL={resp_crcl:02X}")

        client_socket.send(response_packet)

        # cont = input("\nKeep server running? (y/n): ").strip().lower()
        # if cont != 'y':
        #     print("Server shutting down.")
        #     break

except Exception as e:
    print(f"Error: {e}")
finally:
    try: client_socket.close()
    except: pass
    server_socket.close()
