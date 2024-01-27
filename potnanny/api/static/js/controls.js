const CONTROL_DEFAULT = {
    name: null,
    outlet: null,
    device_id: null,
    attributes: {
        input_device_id: null,
        type: null,
        on: {
            condition: null,
            threshold: null,
            seconds: 0,
        },
        off: {
            condition: null,
            threshold: null
        }
    }
};

var inputDevice = {reports: []};
const selectChoices = [
  ['>', 'greater than'],
  ['>=', 'greater than, or equal to'],
  ['<', 'less than'],
  ['<=', 'less than, or equal to'],
  ['==', 'equal to'],
];


var Control = {
    list: [],
    current: CONTROL_DEFAULT,

    loadList: function() {
        let route = API_URI + "/controls";
        return fetch(route, {
            method: "GET",
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json"
            }
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                return {msg: []};
            }
        }).then(function(data) {
            Control.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    load: function(id) {
        Control.current = CONTROL_DEFAULT;
        for (let o of Control.list) {
            if (o.id == id) {
                Control.current = o;
                break;
            }
        }
    },
    loadDeviceOutlet: function(device, outlet) {
        Control.current = CONTROL_DEFAULT;
        for (let o of Control.list) {
            if (o.device_id == device && o.outlet == outlet) {
                Control.current = o;
                break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/controls";

        if (Control.current.id) {
            method = "PATCH";
            route += "/" + Control.current.id
        }

        if (Control.current.attributes.on.seconds && Control.current.attributes.on.seconds > 0) {
            Control.current.attributes.off = {};
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
              "X-CSRF-Token": CSRF_TOKEN,
              "Content-Type": "application/json",
              "Accept": "application/json",
            },
            body: JSON.stringify(Control.current)
        }).then(function(response) {
            if (response.ok) {
              return response.json();
            }
        }).then(function(data) {
            Control.current = CONTROL_DEFAULT;
            Control.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/controls/" + Control.current.id;
        return fetch(route, {
            method: "DELETE",
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
            Control.current = CONTROL_DEFAULT;
        }).catch(function(err) {
            console.log(err);
        })
    },
}


const updateMeasurementChoices = function() {
    var i = document.getElementById('ctrl-input-device');
    if (i.value != null) {
        Device.list.map(function(d) {
            if (d.id == parseInt(i.value)) {
                inputDevice = d;
            }
        })

        var e = document.getElementById('ctrl-mchoices');
        var content = [m("option"), inputDevice.reports.map(function(c) {
            return m("option", {
                value: c,
                selected: (Control.current.attributes.type == c) ? true : false
            }, c);
        })]

        m.render(e, content);
    }
}

const toggleTimedOn = function() {
    let e = document.getElementById('ctrl-on-timed');
    if (e.checked) {
        document.getElementById('ctrl-seconds-block').style.display = "block";
        document.getElementById('ctrl-off-block').style.display = "none";
        document.getElementById('ctrl-off-condition').required = false;
        document.getElementById('ctrl-off-threshold').required = false;
        document.getElementById('ctrl-on-seconds').required = true;
    } else {
    Control.current.attributes.on.seconds = 0;
        document.getElementById('ctrl-seconds-block').style.display = "none";
        document.getElementById('ctrl-off-block').style.display = "block";
        document.getElementById('ctrl-on-seconds').required = false;
        document.getElementById('ctrl-off-condition').required = true;
        document.getElementById('ctrl-off-threshold').required = true;
    }
}


const submitControlForm = function() {
    Control.save();
    hideModal();
    Control.current = CONTROL_DEFAULT;
    setTimeout(function() { window.location.reload(); }, 1200);
    Control.loadList();
}


const controlForm = function(device, outletName) {
    device = parseInt(device);
    let outlet = parseInt(outletName.split("_")[1]);
    
    console.log("Device:" + device + " Outlet:" + outlet);
    Device.load(device);
    Control.loadDeviceOutlet(device, outlet);
    const room = Number(Device.current.room_id);

    if (Control.current.device_id == null) {
        Control.current.device_id = device;
    }
    if (Control.current.outlet == null) {
        Control.current.outlet = outlet;
    }

    var form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
        }}, [
        m("div", [
            m("label.form-label", "Control Name"),
            m("input[type=text].form-control", {
                required: true,
                value: Control.current.name,
                onchange: function(e) {
                    Control.current.name = e.target.value;
                }
            })
        ]),
        m("div.row.row-cols-2.mt-2", [
            m("div.col", [
                m("label.form-label", "Input device"),
                m("select.form-control", {
                    id: "ctrl-input-device",
                    required: true,
                    onchange: function(e) {
                        Control.current.attributes.input_device_id = parseInt(e.target.value);
                        Device.load(parseInt(e.target.value));
                        updateMeasurementChoices();
                    },
                }, [
                    m("option"), Device.list.map(function(d) {
                        return (d.room_id != room || d.id == device) ? null : m("option", {
                            value: d.id,
                            selected: (Control.current.attributes.input_device_id == d.id) ? true : false
                        }, d.name);
                    })
                ])
            ]),
            m("div.col", [
                m("label.form-label", "Measurement"),
                m("select.form-control", {
                    id: "ctrl-mchoices",
                    onchange: function(e) {
                        Control.current.attributes.type = e.target.value;
                    },
                }, [m("option"), Device.current.reports.map(function(r) {
                    return m("option", {
                        value: r,
                        selected: (Control.current.attributes.type == r) ? true : false,
                    }, r);
                })])
            ])
        ]),
        m("div.card.mt-2", {id: "ctrl-on-block"}, [
            m("div.card-header", [
                "Outlet ON",
                m("span", {style: {float: "right"}}, [
                    m("label.form-checkbox-label.mr-2", {
                        for: "ctrl-on-timed"}, "timed ON"
                    ),
                    m("input[type=checkbox].form-checkbox-control", {
                        id: "ctrl-on-timed",
                        checked: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? true : false,
                        onchange: function(e) {
                            toggleTimedOn();
                        }
                    })
                ])
            ]),
            m("div.card-body", [
                m("div.row.row-cols-2", [
                    m("div.col",
                    m("select.form-control.col", {
                        required: true,
                        onchange: function(e) {
                            Control.current.attributes.on.condition = e.target.value;
                        }}, [
                            m("option"), selectChoices.map(function(c) {
                                return m("option", {
                                    value: c[0],
                                    selected: (Control.current.attributes.on.condition == c[0]) ? true : false,
                                }, c[1]);
                            })
                        ]),
                    ),
                    m("div.col",
                    m("input[type=number][step=any].form-control", {
                        required: true,
                        value: Control.current.attributes.on.threshold,
                        onchange: function(e) {
                            Control.current.attributes.on.threshold = parseFloat(e.target.value);
                        }
                    })
                )
            ]),
            m("div.row.row-cols-2.mt-2", [
                m("div.col", {
                    id: "ctrl-seconds-block",
                    style: {
                        display: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? "block" : "none",
                    },
                }, [
                    m("label.form-label.mt-3", "ON seconds"),
                    m("input[type=number][step=any].form-control.col", {
                        id: "ctrl-on-seconds",
                        min: 1,
                        max: 300,
                        step: 1,
                        required: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? true : false,
                        value: Control.current.attributes.on.seconds,
                        onchange: function(e) {
                            Control.current.attributes.on.seconds = parseFloat(e.target.value);
                        }
                    })
                ])
            ]),

            ]),
        ]),
        m("div.card.mt-2", {
            id: "ctrl-off-block",
            style: {
                display: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? "none" : "block",
            }}, [
                m("div.card-header", "Outlet OFF"),
                m("div.card-body",
                m("div.row.row-cols-2", [
                    m("div.col", [
                        m("select.form-control", {
                            id: "ctrl-off-condition",
                            required: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? false : true,
                            onchange: function(e) {
                                Control.current.attributes.off.condition = e.target.value;
                            }
                        }, [m("option"), selectChoices.map(function(c) {
                            return m("option", {
                                value: c[0],
                                selected: (Control.current.attributes.off.condition == c[0]) ? true : false,
                            }, c[1]);
                        })])
                    ]),
                    m("div.col",
                    m("input[type=number][step=any].form-control", {
                        id: "ctrl-off-threshold",
                        required: ("seconds" in Control.current.attributes.on && Control.current.attributes.on.seconds > 0) ? false : true,
                        value: Control.current.attributes.off.threshold,
                        onchange: function(e) {
                            Control.current.attributes.off.threshold = parseFloat(e.target.value);
                        }
                    })
                )
            ])
            )
        ]),
        m("div.row.row-cols-2.mt-3", [
            m("div.col",
                m("button[type=submit].btn.btn-primary.form-control", {
                    onclick: function() {
                        submitControlForm();
                    },
                }, "Save"),
            ),
            (Control.current.id) ? m("div.col",
            m("button.btn.btn-outline-danger.form-control", {
                onclick: function(e) {
                    e.preventDefault();
                    if (confirm("Are you sure you want to delete this control?")) {
                        Control.delete();
                        hideModal();
                        Control.current = CONTROL_DEFAULT;
                        Control.loadList();
                        setTimeout(function() { window.location.reload(); }, 1500);
                    }
                }
            }, "Delete")) : null
        ])
    ]);

    showModal(form);
    updateMeasurementChoices();
}

// preload models
Control.loadList();
