import socket
import uselect
import ujson
import machine
import utime as time

from hardware import LampHardware


class OpenDeskLamp:

    headers = b"Connection: close\r\n"

    def __init__(self):
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

        self.hardware = LampHardware()

        self.sock = socket.socket()
        self.sock.bind(addr)
        self.sock.listen(1)

        self.sock_list = [self.sock]
        self.endpoints = dict()

    @staticmethod
    def parse_method(sock):
        method, target, *_ = sock.readline().decode("utf-8").replace('\n', ' ').replace('\r', '').split(" ")

        content_length = None

        while True:
            header = sock.readline().decode("utf-8")
            if header == "" or header == "\r\n":
                break
            if "Content-Length:" in header:
                ll = header.replace(" ", "").replace("Content-Length:", "").strip()
                return method, target, int(ll)

        return method, target, None

    def add_route(self, target, methods):
        self.endpoints[target] = methods

    def serve(self):
        readable, _, _ = uselect.select(self.sock_list, [], [], 0.001)
        for s in readable:
            if s is self.sock:
                client_socket, address = self.sock.accept()
                self.sock_list.append(client_socket)
                print("Connection from", address)
            else:
                method, target, content_length = self.parse_method(s)
                print("Reqeust for ", target, method)
                if target in self.endpoints:
                    supported_methods = self.endpoints[target]
                    if method in supported_methods:
                        callback = supported_methods[method]
                        print("Handling", method, "for endpoint", target)
                        if method == "POST":
                            while True:
                                header = s.readline().decode("utf-8")
                                if header == "" or header == "\r\n":
                                    break
                            content = s.read(content_length).decode("utf-8")
                            callback(s, content)
                        else:
                            callback(s)
                    else:
                        print("illegal method", method, "for endpoint", target)
                        s.send(b'HTTP/1.0 405 Method Not Allowed' + self.headers + b'\r\n\r\n')

                s.close()
                self.sock_list.remove(s)

    def serve_setup(self, sock):
        with open("/www/setup.html", "r") as fp:
            html = fp.read()
        sock.send(b'HTTP/1.0 200 OK\r\n' + self.headers + b'Content-type: text/html\r\n\r\n')
        sock.send(html.encode("utf-8"))

    def serve_index(self, sock):
        with open("/www/index.html", "r") as fp:
            html = fp.read()

        sock.send(b'HTTP/1.0 200 OK\r\n' + self.headers + b'Content-type: text/html\r\n\r\n')
        sock.send(html.encode("utf-8"))

    def serve_register_credentials(self, sock, content):
        params = self.parse_query_string(content)

        if "ssid" in params and "passwd" in params:

            with open("/creds", "w") as fp:
                fp.write(params["ssid"])
                fp.write("\n")
                fp.write(params["passwd"])

            print("Wrote new credentials:", params["ssid"], params["passwd"])

            with open("/www/restart.html", "r") as fp:
                html = fp.read()

            sock.send(b'HTTP/1.0 200 OK\r\n' + self.headers + b'Content-type: text/html\r\n\r\n')
            sock.send(html.encode("utf-8"))

            sock.close()
            time.sleep(0.6)
            machine.reset()

        else:
            sock.send(b'HTTP/1.0 400 Bad Request\r\n' + self.headers + b'\r\n\r\n')

    @staticmethod
    def parse_query_string(content):
        params = dict()
        try:
            for param in content.split('&'):
                key, value = param.split("=")
                params[key] = value
        except Exception as exc:
            print("could not parse query:", exc)
        return params

    def serve_status(self, sock):
        sock.send(b'HTTP/1.0 200 OK\r\n' + self.headers + b'Content-type: text/json\r\n\r\n')
        sock.send(ujson.dumps({
            "on": self.hardware.on,
            "brightness": self.hardware.brightness(),
            "color": self.hardware.color()
        }))

    def serve_style(self, sock):
        sock.send(b'HTTP/1.0 200 OK\r\n' + self.headers + b'Content-type: text/css\r\n\r\n')
        with open("/www/open-desk-lamp.css", "r") as fp:
            css = fp.read()
        sock.send(css.encode("utf-8"))

    def loop_forever(self):
        try:
            with self.hardware:
                self.hardware.pulse(duration=0.5, n=3)
                while True:
                    for i in range(10):
                        self.hardware.update()
                    self.serve()
        finally:
            self.sock.close()


