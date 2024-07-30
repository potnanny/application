/** DEFAULTS **/
const ACTION_DEFAULT = {
    name: null,
    room_id: null,
    interface: null,
    attributes: {
        condition: null,
        threshold: null,
        input_device_id: null,
        input_type: null,
        sleep_minutes: null,
    },
};

const DEVICE_DEFAULT = {
    name: null,
    room_id: null,
    interface: null,
    attributes: {},
    reports: [],
    plugin: {}
};

const selectChoices = [
  ['>', 'greater than'],
  ['>=', 'greater than, or equal to'],
  ['<', 'less than'],
  ['<=', 'less than, or equal to'],
  ['==', 'equal to'],
];

const updateMeasurementChoices = function() {
    var i = document.getElementById('action-input-device');
    console.log("input device: " + i);
    if (i.value == null || i.value == undefined || i.value == "") {
        Device.current = DEVICE_DEFAULT;
        Device.list.map(function(d) {
            Device.current.reports = Device.current.reports.concat(d.reports);
        })
        Device.current.reports = Array.from(new Set(Device.current.reports));
    } else {
        Device.load(parseInt(i.value));
    }

    var e = document.getElementById('action-mchoices');
    var content = [m("option"), Device.current.reports.map(function(c) {
        return m("option", {
            value: c,
            selected: (Action.current.attributes.input_type == c) ? true : false
        }, c);
    })]

    m.render(e, content);
}

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
            var myList = []
            data.msg.map(function(d) {
                if (d.room_id != null) {
                    myList.push(d);
                }
            })
            Device.list = myList;
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
    }
}

var ActionPlugin = {
    list: [],
    loadList: function() {
        let route = API_URI + "/plugins";
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
            // filter out only the Action plugins
            ActionPlugin.list = data.msg.action;
        }).catch(function(err) {
            console.log(err);
        })
    }
}

var Action = {
    list: [],
    current: ACTION_DEFAULT,

    loadList: function() {
        let route = API_URI + "/actions";
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
            Action.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    load: function(id) {
        Action.current = ACTION_DEFAULT;
        for (let o of Action.list) {
            if (o.id == id) {
                Action.current = o;
                break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/actions";

        if (Action.current.id) {
            method = "PATCH";
            route += "/" + Action.current.id
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(Action.current)
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Action.current = data.msg;
            Action.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/actions/" + Action.current.id;
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
            Action.current = ACTION_DEFAULT;
            Action.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    }
}

/** FORMS/MODALS **/
var actionFormModal = function(id = undefined) {
    if (id) {
        Action.load(id);
    }
    var form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            Action.save();
            hideModal();
            setTimeout(function() { window.location.reload(); }, 2000);
        }}, [
        // action name
        m("div.row.row-cols-1.mt-2",
            m("div.col",
                m("input[type=text][required].form-control", {
                    id: "name",
                    placeholder: "action name",
                    value: Action.current.name,
                    onchange: function(e) {
                        Action.current.name = sanitizeInput(e.target.value);
                    }}
                ),
            )
        ),
        // action input device
        m("div.row.row-cols-1.mt-2", [
            m("div.col", [
                m("label.form-label", "Input device (optional)"),
                m("select.form-control", {
                    id: "action-input-device",
                    onchange: function(e) {
                        Action.current.attributes.input_device_id = parseInt(e.target.value);
                        try {
                            Device.load(parseInt(e.target.value));
                        } catch(error) {
                            console.log(error);
                        }
                        updateMeasurementChoices();
                    },
                }, [
                    m("option"), Device.list.map(function(d) {
                        if (d.room_id) {
                            return m("option", {
                                value: d.id,
                                selected: (Action.current.attributes.input_device_id == d.id) ? true : false
                            }, d.name);
                        }
                    })
                ])
            ]),

        ]),
        // action condition and threshold
        m("div.row.row-cols-1.row-cols-md-3.mt-2", [
            m("div.col", [
                m("label.form-label", "Input Measurement"),
                m("select.form-control", {
                    id: "action-mchoices",
                    required: true,
                    onchange: function(e) {
                        Action.current.attributes.input_type = e.target.value;
                    },
                }, [m("option"), Device.current.reports.map(function(r) {
                    return m("option", {
                        value: r,
                        selected: (Action.current.attributes.input_type == r) ? true : false,
                    }, r);
                })])
            ]),
            m("div.col", [
                m("label.form-label", "Action condition"),
                m("select.form-control.col", {
                    required: true,
                    onchange: function(e) {
                        Action.current.attributes.condition = e.target.value;
                    }}, [
                        m("option"), selectChoices.map(function(c) {
                            return m("option", {
                                value: c[0],
                                selected: (Action.current.attributes.condition == c[0]) ? true : false,
                            }, c[1]);
                        })
                    ]),
                ]),
            m("div.col", [
                m("label.form-label", "Action threshold"),
                m("input[type=number][step=any].form-control", {
                    required: true,
                    value: Action.current.attributes.threshold,
                    onchange: function(e) {
                        Action.current.attributes.threshold = parseFloat(e.target.value);
                    }
                })
            ]),
        ]),
        // plugin interface
        m("div.row.row-cols-1.mt-2",
            m("div.col", [
                m("label.form-label", "Plugin"),
                m("select.form-control", {
                    id: "action-interface",
                    required: true,
                    onchange: function(e) {
                        Action.current.interface = e.target.value;
                    },
                }, [
                    m("option"), ActionPlugin.list.map(function(p) {
                        return m("option", {
                            value: p.interface,
                            selected: (Action.current.interface == p.interface) ? true : false
                        }, p.name);
                    })
                ]),
            ])
        ),
        // action sleep timer
        m("div.row.row-cols-2.mt-2", [
            m("div.col", [
                m("label.form-label", "Sleep Minutes"),
                m("input[type=number].form-control", {
                    value: Action.current.attributes.sleep_minutes,
                    onchange: function(e) {
                        Action.current.attributes.sleep_minutes = parseInt(e.target.value);
                    }},
                )
            ])
        ]),
        // save and delete buttons
        m("div.row.row-cols-2.mt-4", [
            m("div.col",
              m("button[type=submit].submit.btn.btn-primary.form-control", "Save")
            ),
            (Action.current.id) ? m("div.col",
              m("button.btn.btn-outline-danger.form-control", {
                onclick: function(e) {
                  e.preventDefault();
                  if (confirm("Are you sure you want to delete this Action and all of its data?")) {
                    Action.delete();
                    hideModal();
                    setTimeout(function() { window.location.reload(); }, 1500);
                  }
                }
                }, "Delete")
            ) : null
        ])
    ]);

    showModal(form);
    updateMeasurementChoices();
}

/** PRELOAD MODELS **/
setTimeout(function() { Action.loadList(); ActionPlugin.loadList(); Device.loadList(); }, 300);
