const SCHEDULE_DEFAULT = {
  name: null,
  device_id: null,
  outlet: null,
  days: 127,
  on_time: "00:00",
  off_time: "00:00"  };


var Schedule = {
    list: [],
    current: {},
    loadList: function() {
        let route = API_URI + "/schedules";
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
                return {msg: []};
            }
        }).then(function(data) {
            Schedule.list = data.msg;
        }).catch(function(err) {
            console.log("schedule whoopsie! " + err);
        })
    },
    load: function(id) {
        Schedule.current = SCHEDULE_DEFAULT;
        for (let o of Schedule.list) {
            if (o.id == id) {
              Schedule.current = o;
              break;
            }
        }
    },
    loadDeviceOutlet: function(device, outlet) {
        Schedule.current = SCHEDULE_DEFAULT;
        Schedule.current.device_id = device;
        Schedule.current.outlet = outlet;
        for (let o of Schedule.list) {
            if (o.device_id == device && o.outlet == outlet) {
              Schedule.current = o;
              break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/schedules";

        if (Schedule.current.id) {
            method = "PATCH";
            route += "/" + Schedule.current.id
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
              "X-CSRF-Token": CSRF_TOKEN,
              "Content-Type": "application/json",
              "Accept": "application/json",
            },
            body: JSON.stringify(Schedule.current)
        }).then(function(response) {
            if (response.ok) {
              return response.json();
            }
        }).then(function(data) {
            Schedule.current = SCHEDULE_DEFAULT;
            Schedule.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/schedules/" + Schedule.current.id;
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
            Schedule.current = SCHEDULE_DEFAULT;
            Schedule.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    }
}


const Weekdays = [
    ['Sun', 64],
    ['Mon', 32],
    ['Tue', 16],
    ['Wed', 8],
    ['Thu', 4],
    ['Fri', 2],
    ['Sat', 1] ];


const scheduleForm = function(device, outlet) {
    Schedule.loadDeviceOutlet(device, outlet);

    var form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            Schedule.save();
            hideModal();
            setTimeout(function() { window.location.reload(); }, 1500);
        }},
        m("div.container", [
            m("div.row", [
                m("label.form-label", "Schedule Name"),
                m("input[type=text].form-control", {
                    required: true,
                    value: Schedule.current.name,
                    onchange: function(e) {
                        Schedule.current.name = e.target.value;
                    }
                })
            ]),
            m("div.row.row-cols-2", [
                m("div.col.m-0.p-1", [
                    m("label[for=on_time].form-label.mt-3", "Outlet ON"),
                    m("input[type=time].form-control", {
                        id: "on_time",
                        required: true,
                        value: Schedule.current.on_time,
                        onchange: function(e) {
                            Schedule.current.on_time = e.target.value;
                        }
                    })
                ]),
                m("div.col.m-0.p-1", [
                    m("label[for=off_time].form-label.mt-3", "Outlet OFF"),
                    m("input[type=time].form-control", {
                        id: "off_time",
                        required: true,
                        value: Schedule.current.off_time,
                        onchange: function(e) {
                            Schedule.current.off_time = e.target.value;
                        }
                    })
                ])
            ]),
            m("div.row.row-cols-7.mt-3.text-center", [
                Weekdays.map(function(w) {
                    return m("div.col", [
                        m("input[type=checkbox].form-check-input", {
                            checked: Boolean(Schedule.current.days & w[1]),
                            onchange: function(e) {
                                if (e.target.checked) {
                                    Schedule.current.days += w[1];
                                } else {
                                    Schedule.current.days -= w[1];
                                }
                            }
                        }),
                        m("label.form-check-label.fw-light", w[0])
                    ]);
                })
            ]),
            m("div.row.row-cols-2.mt-4", [
                m("div.col",
                    m("input[type=submit].btn.btn-primary.form-control", {
                        value: "Save"
                    }),
                ),
                (Schedule.current.id) ? m("div.col",
                    m("button.btn.btn-outline-danger.form-control", {
                        onclick: function(e) {
                            e.preventDefault();
                            if (confirm("Are you sure you want to delete this schedule?")) {
                                Schedule.delete();
                                hideModal();
                                Schedule.current = SCHEDULE_DEFAULT;
                                Schedule.loadList();
                                setTimeout(function() { window.location.reload(); }, 1500);
                            }
                        }
                    }, "Delete")
                ) : null
            ])
        ])
    );

    showModal(form);
}

// preload models
Schedule.loadList();
