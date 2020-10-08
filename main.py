from open_desk_lamp import OpenDeskLamp


app = OpenDeskLamp()

app.add_route("/setup", {"GET": app.serve_setup})
app.add_route("/", {"GET": app.serve_index})
app.add_route("/register_credentials", {"POST": app.serve_register_credentials})
app.add_route("/state", {"GET": app.serve_state, "PUT": app.set_state})
app.add_route("/open-desk-lamp.css", {"GET": app.serve_style})
app.add_route("/detect", {"GET": app.serve_detect})
app.add_route("/config", {"GET": app.serve_config})
app.loop_forever()

