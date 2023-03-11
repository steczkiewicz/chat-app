import socket
import select
from threading import Thread
import json

IP = '127.0.0.1'
PORT = 12345
mode = "tcp"

def tcp_receive(sock):
    data = sock.recv(1024)
    data = data.decode("utf-8")
    data = json.loads(data)
    return data["name"], data["msg"]

def tcp_send(sock, data, name):
    msg = {"name": name, "msg": data}
    sock.sendall(json.dumps(msg).encode())

def udp_receive(sock):
    data = sock.recv(1024)
    data = data.decode("utf-8")
    data = json.loads(data)
    return data["name"], data["msg"]

def udp_send(sock, data, name):
    msg = {"name": name, "msg": data}
    sock.sendto(json.dumps(msg).encode(), (IP, PORT))

def receive(tcp_sock, udp_sock):
    while True:
        ready_socks, _, _ = select.select([tcp_sock, udp_sock], [], [])

        for sock in ready_socks:
            try:
                if sock is tcp_sock:
                    name, msg = tcp_receive(sock)
                elif sock is udp_sock:
                    name, msg = udp_receive(sock)
            except (ConnectionResetError, ConnectionAbortedError):
                print('Error! Server disconnected.')
                exit(1)

            print(name + ": " + msg)

if __name__ == '__main__':
    print('PYTHON CLIENT')

    name = input("Choose your name: ")

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((IP, PORT))
    tcp_send(tcp_sock, "", name)

    _, tcp_port = tcp_sock.getsockname()

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((IP, tcp_port))

    print("Start typing to talk!")

    thread = Thread(target=receive, args=(tcp_sock, udp_sock))
    thread.start()

    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            tcp_sock.close()
            udp_sock.close()
            exit(1)

        if not line:
            continue

        if line == "!U":
            mode = "udp"
            continue

        if mode == "tcp":
            tcp_send(tcp_sock, line, name)
        elif mode == "udp":
            udp_send(udp_sock, line, name)

        mode = "tcp"