if target == "/register_credentials":
    if method == "POST":
        content = s.recv(content_length * 8).decode("utf-8")
        print(content.split("\r\n\r\n")[1].split('&'))
        with open("restart.html", "r") as fp:
            html = fp.read()

        s.send(b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        s.send(html.encode("utf-8"))
    else:
        print("illegal method ", method)
        s.send(b'HTTP/1.0 405 Method Not Allowed\r\n\r\n')

elif target == "/status":
    if method == "GET" or method == "HEAD":
        s.send(b'HTTP/1.0 200 OK\r\nContent-type: text/json\r\n\r\n')
        s.send(ujson.dumps({"on": lamp.on, "brightness": lamp.brightness(), "color": lamp.color()}))
    else:
        print("illegal method ", method)
        s.send(b'HTTP/1.0 405 Method Not Allowed\r\n\r\n')


elif target == "/" or target == "" or target == "/setup":
    if method == "GET" or method == "HEAD":
        with open("setup.html", "r") as fp:
            html = fp.read()
        print("Get Request to /")
        s.send(b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        s.send(html.encode("utf-8"))
    else:
        print("illegal method ", method)
        s.send(b'HTTP/1.0 405 Method Not Allowed\r\n\r\n')

else:
    print("Received Request to unknown target", target)
    s.send(b'HTTP/1.0 404 Not Found\r\n\r\n')