/** DEFAULTS **/
const DEVICE_DEFAULT = {
    name: null,
    room_id: null,
    interface: null,
    attributes: {},
    reports: [],
    plugin: {}
};


/** MODELS **/
var Device = {
    list: [],
    current: DEVICE_DEFAULT,

    loadList: function() {
        let route = API_URI + "/devices";
        return fetch(route, {
            method: "GET",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json"
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Device.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    load: function(id) {
        Device.current = DEVICE_DEFAULT;
        for (let o of Device.list) {
            if (o.id == id) {
                Device.current = o;
                break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/devices";

        if (Device.current.id) {
            method = "PATCH";
            route += "/" + Device.current.id
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(Device.current)
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Device.current = data.msg;
            Device.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/devices/" + Device.current.id;
        return fetch(route, {
            method: "DELETE",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Device.current = DEVICE_DEFAULT;
            Device.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    pollCurrent: function(pk = undefined) {
        if (! pk) {
            pk = Device.current.id;
        }
        let route = API_URI + "/devices/" + pk + "/poll";
        console.log(route);
        return fetch(route, {
            method: "POST",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            let r = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    scanKeycodePromise: function() {
        let route = API_URI + "/devices/" + Device.current.id + "/keycode";
        return fetch(route, {
            method: "GET",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        })
    },
    switchDevice: function(pk, outlet, state) {
        Device.load(pk);
        let url = API_URI + "/devices/" + pk + "/" + outlet;
        url += (state == 0) ? "/off" : "/on";

        return fetch(url, {
            method: "POST",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            let d = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    }
}


/** FORMS/MODALS **/
var deviceNameModal = function(id = undefined) {

    if (id) { Device.load(Number(id)); }

    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            hideModal();
            Device.save();
            setTimeout(function() { Device.loadList(); }, 300);
            setTimeout(function() { window.location.reload(); }, 500);
        }}, [
        m("input[type=text][required][placeholder=Device Name].form-control", {
            id: "devicename",
            value: Device.current.name,
            onchange: function(e) {
                Device.current.name = e.target.value;
            }
        }),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);

    showModal(form)
}


/** FORMS/MODALS **/
var deviceFormModal = function(id) {
    Device.load(id);
    var newRoom = false;
    var form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            setTimeout(function() {
                Device.pollCurrent(Device.current.id);
            }, 200);
            Device.save();
            hideModal();
            setTimeout(function() { window.location.reload(); }, 6000);

        }}, [
      m("input[type=text][required].form-control", {
        id: "name",
        value: Device.current.name,
        onchange: function(e) {
          Device.current.name = e.target.value;
        }}
      ),
      m("label[for=room].form-label.mt-3", "Room Assignment"),
      m("select.form-select", {
        id: "room",
        onchange: function(e) {
          newRoom = true;
          Device.current.room_id = parseInt(e.target.value);
        }}, [ Room.list.map(function(r) {
          return m((r.id == Device.current.room_id) ? "option[selected]" : "option", {value: r.id}, r.name);
      }), m((Device.current.room_id == null) ? "option[selected]" : "option", {value: null}, "")]
      ),
      ("is_key_required" in Device.current.plugin && Device.current.plugin.is_key_required == true) ?
        m("div.input-group.mt-3", [
          m("input[type=text][required][placeholder=Key Code]", {
            id: "key_code",
            class: "form-control",
            value: Device.current.attributes.key_code,
            disabled: (Device.current.attributes.key_code == null) ? false : true,
            onchange: function(e) {
              Device.current.attributes.key_code = e.target.value;
            }},
          ),
          m("button.btn.btn-outline-primary", {
            onclick: function(e) {
              e.preventDefault();
              this.disabled = true;
              let element = document.getElementById('key_code');
              alert("The light on the outlet will blink blue. Once that happens, press the button on the outlet 3-4 times");
              Device.scanKeycodePromise().then(function(result) {
                  if (result.ok) {
                     return result.json();
                  }
              }).then(function(data) {
                  let key = data.msg;
                  element.value = key;
                  element.disabled = true;
                  Device.current.attributes.key_code = key;
              }).catch(function(err) {
                  console.log(err);
              });
              this.disabled = false;
            }
          }, "Capture")
        ])
      : null,
      m("div.mt-4.row.row-cols-2.mt-2", [
        m("div.col", [
          m("label[for=plugin1].form-label", "Plugin"),
          m("input[type=text][disabled].form-control", {
            id: 'plugin1',
            value: Device.current.interface }),
        ]),
        m("div.col", [
          m("label[for=address1].form-label", "Address"),
          ('address' in Device.current.attributes) ?
            m("input[type=text][disabled].form-control", {
              id: 'address1',
              value: Device.current.attributes.address })
          : null
        ]),
      ]),
      m("div.mt-4.row.row-cols-2", [
        m("div.col",
          m("button[type=submit].submit.btn.btn-primary.form-control", "Save")
        ),
        m("div.col",
          m("button.btn.btn-outline-danger.form-control", {
            onclick: function(e) {
              e.preventDefault();
              if (confirm("Are you sure you want to delete this device and all of its data?")) {
                Device.delete();
                hideModal();
                setTimeout(function() { window.location.reload(); }, 3000);
              }
            }
          }, "Delete")
        )
      ])
    ]);

    showModal(form);
}

/** PRELOAD MODELS **/
setTimeout(function() { Device.loadList(); }, 300);
