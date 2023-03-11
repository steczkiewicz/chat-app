import socket
import json
from threading import Thread

IP = '127.0.0.1'
PORT = 12345

clients = {}
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udp_sock.bind((IP, PORT))


def accept_tcp_connections(tcp_sock):
    while True:
        try:
            client_sock, client_addr = tcp_sock.accept()
            print(f"New connection from {client_addr[0]}:{client_addr[1]}")
            clients[client_addr] = client_sock
            client_thread = Thread(target=handle_tcp_client, args=(client_sock, client_addr))
            client_thread.start()
        except OSError as e:
            print(f"Error accepting TCP connection: {e}")


def handle_tcp_client(client_sock, client_addr):
    while True:
        try:
            data = client_sock.recv(1024)
        except ConnectionResetError:
            remove_client(client_addr)
            return

        data_dec = json.loads(data.decode("utf-8"))
        if data_dec["msg"] == "":
            print(f"User {data_dec['name']} connected!")
            continue

        for other_client_sock in clients.values():
            if other_client_sock != client_sock:
                other_client_sock.sendall(data)

        print(f"[TCP] [{data_dec['name']}] {data_dec['msg']}")


def remove_client(client_addr):
    print(f"Client {client_addr[0]}:{client_addr[1]} disconnected.")
    clients.pop(client_addr)


def handle_udp_messages(udp_sock):
    while True:
        data, addr = udp_sock.recvfrom(1024)
        data_dec = json.loads(data.decode("utf-8"))

        for client_addr, client_sock in clients.items():
            if client_addr != addr:
                client_sock.sendto(data, client_addr)

        print(f"[UDP] [{data_dec['name']}] {data_dec['msg']}")


def run_server():
    print("PYTHON SERVER")
    print(f"Server listening on {IP}:{PORT}")
    tcp_sock.bind((IP, PORT))
    tcp_sock.listen()

    Thread(target=accept_tcp_connections, args=(tcp_sock,)).start()
    Thread(target=handle_udp_messages, args=(udp_sock,)).start()


if __name__ == "__main__":
    run_server()
