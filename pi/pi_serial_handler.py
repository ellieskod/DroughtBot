#!/usr/bin/env python3

import requests
import serial
import struct

PORT = '/dev/ttyUSB0'
BAUD = 115200
active_transfers = {}

def parse_payload(buffer):

    if len(buffer) < 13: 
        return None, buffer
    
    try:
        msg_type, transfer_id, chunk_idx, chunk_count = struct.unpack('<BIII', buffer[:13])
    except:
        return None, buffer[1:]
    
    if msg_type != 8:
        return None, buffer[1:]
    
    payload = buffer[13:]
    return {
        'transfer_id': transfer_id,
        'chunk_index': chunk_idx,
        'chunk_count': chunk_count,
        'data': payload
    }, b''  # Return remaining buffer

# assemble chunks into complete payloads
def process_chunk(chunk):
    tid = chunk['transfer_id']
    
    if tid not in active_transfers:
        if chunk['chunk_index'] != 0:
            return None
        active_transfers[tid] = {}
    
    active_transfers[tid][chunk['chunk_index']] = chunk['data']
    
    # all chunks received?
    if len(active_transfers[tid]) == chunk['chunk_count']:
        payload = b''.join(active_transfers[tid][i] for i in range(chunk['chunk_count']))
        del active_transfers[tid]
        return payload
    
    return None

#todo switch case over message types

def handle_payload(payload):
    
    print(f"Got payload ({len(payload)} bytes): {payload}")
    
    try:
        # parse payload as JSON and POST it to the local server
        import json
        data = json.loads(payload.decode('utf-8'))
        print(f"POSTing JSON data: {data}")
        requests.post(f'http://localhost/{type(data).__name__}', json=data)
    except:
        pass


if __name__ == '__main__':
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}")
    
    buffer = b''
    try:
        while True:
            if ser.in_waiting:
                buffer += ser.read(ser.in_waiting)
                
                #try to extract chunks from buffer
                while True:
                    chunk, buffer = parse_payload(buffer)
                    if not chunk:
                        break
                    
                    payload = process_chunk(chunk)
                    if payload:
                        handle_payload(payload)
    
    except KeyboardInterrupt:
        print("Done")
    finally:
        ser.close()
