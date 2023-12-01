import socket
import io
import time
import typing
import struct
import homework4
import homework4.logging

def update_timeout(est, dev, round_trip_time):
    if not est:
        est = round_trip_time
        dev = round_trip_time / 2

    if est:
        change = abs(round_trip_time - est)
        est = 0.75 * est + 0.25 * round_trip_time
        dev = 0.75 * dev + 0.25 * change
        
    return est, dev


def send(sock: socket.socket, data: bytes):

    timeout = 1
    dev = 0.0
    est = 0
    packet_total = 0
    chunk_size = homework4.MAX_PACKET - 4
    offsets = range(0, len(data), homework4.MAX_PACKET - 4)
    for chunk in [data[i: i + chunk_size] for i in offsets]:
        header = packet_total.to_bytes(4, byteorder='big')
        packets= header + chunk
        sock.send(packets)
        while True:
            try:
                sock.settimeout(timeout)
                start = time.time()
                data = sock.recv(4)
                if data == header:
                    round_trip_time = time.time() - start
                    est,dev= update_timeout(est, dev, round_trip_time)
                    timeout = est + 3 * dev
                    break
                sock.send(packets)
            except socket.timeout:
                sock.send(packets)
                timeout = timeout * 3
                continue
        packet_total += 1


def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    Total_bytes = 0
    previous_header = []
    while True:
        packet = sock.recv(homework4.MAX_PACKET)
        length_of_packet = 0
        if not packet:
            break
        else:
            length_of_packet = len(packet)
            header = packet[0: 4]
            data= packet[4: length_of_packet]
            sock.send(header)
            if previous_header == header:
                continue
        Total_bytes += length_of_packet - 4
        previous_header = header
        dest.write(data)
        dest.flush()
    return Total_bytes