var SerialNumber = {
    current: "",
    load: function() {
        let route = API_URI + "/serial";
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
            SerialNumber.current = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    }
}
SerialNumber.load();


const pollingIntervalForm = function() {
    Keychain.loadName('settings');

    let form = m("form", {
        onsubmit: function(e) {
              e.preventDefault();
              hideModal();
              Keychain.save();
        }}, [
        m("label.form-label", "Polling Interval"),
        m("input[type=number][required][placeholder=Polling Interval Minutes].form-control", {
              id: "interval",
              min: 2,
              max: 30,
              value: Keychain.current.attributes.polling_interval,
              onchange: function(e) {
                  Keychain.current.attributes.polling_interval = parseInt(e.target.value)
              }
        }),
        m("div.form-text", "How often (in minutes) to poll devices for data."),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);

    showModal(form);
}


const temperatureDisplayForm = function() {
    Keychain.loadName('settings');

    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            Keychain.save();
            modal.hide();
        }}, [
        m("label.form-label", "System Temperature Format"),
        m("select.form-control", {
            id: 'temperature',
            value: Keychain.current.attributes.temperature_display,
            onchange: function(e) {
                Keychain.current.attributes.temperature_display = e.target.value;
            }}, [
        m("option", {
            value: "F",
            selected: (Keychain.current.attributes.temperature_display == "F") ? true : false},
            "Fahrenheit"),
        m("option", {
            value: "C",
            selected: (Keychain.current.attributes.temperature_display == "C") ? true : false},
            "Celsius"),
        ]),
        m("div.form-text", "How temperatures are stored and displayed."),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);
    showModal(form);
}


const leafOffsetForm = function() {
    Keychain.loadName('settings');

    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            hideModal();
            Keychain.save();
        }}, [
        m("label.form-label", "Leaf Temperature Offset"),
        m("input[type=number][required][placeholder=Leaf Temperature Offset].form-control", {
            id: "offset",
            min: -5,
            max: 5,
            value: Keychain.current.attributes.leaf_offset,
            onchange: function(e) {
                Keychain.current.attributes.leaf_offset = parseInt(e.target.value)
            }
        }),
        m("div.form-text", "Leaf temperature offset (in celsius) for V.P.D. calculations."),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);
    showModal(form);
}


const storageDaysForm = function() {
    Keychain.loadName('settings');

    let form = m("form", {
        onsubmit: function(e) {
        e.preventDefault();
        hideModal();
        Keychain.save();
        }}, [
        m("label.form-label", "Measurement Retention"),
        m("input[type=number][required][placeholder=Measurement Storage Days].form-control", {
            id: "storage",
            min: 1,
            max: 365,
            value: Keychain.current.attributes.storage_days,
            onchange: function(e) {
                Keychain.current.attributes.storage_days = parseInt(e.target.value)
            }
        }),
        m("div.form-text", "Number of days device measurements should be kept in the database."),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);
    showModal(form);
}


const graphHoursForm = function() {
    Keychain.loadName('settings');

    let form = m("form", {
        onsubmit: function(e) {
        e.preventDefault();
        hideModal();
        Keychain.save();
        }}, [
        m("label.form-label", "Graph Hours"),
        m("input[type=number][required][placeholder=Graph Hours].form-control", {
            id: "storage",
            min: 1,
            max: 48,
            value: Keychain.current.attributes.graph_hours,
            onchange: function(e) {
                Keychain.current.attributes.graph_hours = parseInt(e.target.value)
            }
        }),
        m("div.form-text", "Number of hours to display in graphs."),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);
    showModal(form);
}


const serialNumberForm = function() {
    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
        }}, [
        m("label.form-label", "Serial Number"),
        m("input[readonly][placeholder=Raspberry Pi Serial Number].form-control", {
            id: "serial",
            value: SerialNumber.current,
        }),
    ]);
    showModal(form);
}


const restartWorker = function() {
    if (confirm("This will halt the program for a few moments. Do you really want to restart the worker?")) {
        let route = API_URI + "/restartworker";
        return fetch(route, {
            method: "POST",
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
            // ok
        }).catch(function(err) {
            console.log(err);
        })
    }
}

Keychain.loadList();
