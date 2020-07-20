from open_desk_lamp import OpenDeskLamp


app = OpenDeskLamp()

app.add_route("/setup", {"GET": app.serve_setup})
app.add_route("/", {"GET": app.serve_index})
app.add_route("/register_credentials", {"POST": app.serve_register_credentials})
app.add_route("/status", {"GET": app.serve_status})
app.add_route("/open-desk-lamp.css", {"GET": app.serve_style})
app.loop_forever()

