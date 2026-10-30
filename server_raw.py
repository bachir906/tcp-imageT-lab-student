
import socket
import struct
import time
import cv2
import numpy as np

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length


def recv_exact(sock, n):
    """Read exactly n bytes from a TCP stream."""
    data = bytearray()

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data.extend(packet)

    return bytes(data)


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    try:
        # Wait for the first byte without consuming it, so the timer measures
        # the transfer itself and not the time the client spends preparing the image.
        if not conn.recv(1, socket.MSG_PEEK):
            print("Client closed the connection without sending data.")
            return

        start_time = time.time()

        # TODO 5: Read the exact header bytes using recv_exact (HEADER_SIZE bytes).
        header = recv_exact(conn, HEADER_SIZE)

        if header is None:
            print("Error: connection closed before full header arrived.")
            return

        # TODO 6: Unpack the header fields using struct.unpack()
        height, width, payload_length = struct.unpack('!HHI', header)

        print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

        pixels = height * width
        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match the image dimensions.")
            return

        # TODO 7: Read the exact payload bytes (payload_length) using recv_exact.
        payload = recv_exact(conn, payload_length)

        if payload is None:
            print("Error: connection closed before full image arrived.")
            return

        # TODO 8: Reconstruct the raw numpy array and reshape it to (height, width, channels).
        channels = payload_length // pixels

        if channels not in (1, 3, 4):
            print("Error: unsupported number of image channels.")
            return

        image_array = np.frombuffer(payload, dtype=np.uint8)
        image = image_array.reshape((height, width, channels))

        cv2.imwrite("received_image.png", image)

        # TODO 9: Calculate and log network performance metrics (Latency, Packet loss, Throughput KB/s)
        elapsed = time.time() - start_time

        latency_ms = elapsed * 1000
        packet_loss = 0.0
        throughput_kbps = (payload_length / 1024) / elapsed if elapsed > 0 else 0

        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
        print(f"Metrics | Latency: {latency_ms:.3f} ms | Packet loss: {packet_loss:.2f} % | "
              f"Throughput: {throughput_kbps:.2f} KB/s")

    finally:
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    run_server()
