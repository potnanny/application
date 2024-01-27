/** MODELS **/
var Environment = {
    list: [],

    loadList: function() {
        let route = API_URI + "/environments";
        return fetch(route, {
            method: "GET",
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
            Environment.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    }
}

var RoomEnvironment = {
    current: {
        id: null,
        name: null,
        devices: [],
    },

    loadList: function(pk) {
        let route = API_URI + "/environments/" + pk;
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
            RoomEnvironment.current = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    }
}

const updateEnvironments = function() {
    Environment.list.map(function(room) {
        try {
            let name = document.getElementById('room-' + room.id + '-name');
            name.innerHTML = room.name;

            let created = document.getElementById('room-' + room.id + '-created');
            created.innerHTML = dateFromISO(room.created).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

            for (const [key, value] of Object.entries(room.measurements)) {
                let target = document.getElementById('room-' + room.id + '-' + key);
                let entry = 0;

                if (['temperature','vpd'].indexOf(key) > -1) {
                    entry = value.toFixed(1);
                } else {
                    entry = value.toFixed();
                }

                if (Object.keys(mySuffixes).indexOf(key) > -1) {
                    entry += mySuffixes[key];
                }

                target.innerHTML = entry;
            }
        } catch(err) {
            console.log(err);
        }
    })
}

const updateRoomEnvironments = function() {
    RoomEnvironment.current.devices.map(function(device) {
        try {
            let name = document.getElementById('device-' + device.id + '-name');
            name.innerHTML = device.name;

            try {
                let created = document.getElementById('device-' + device.id + '-created');
                if (device.created != null) {
                    created.innerHTML = dateFromISO(device.created).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
                }
            } catch(err) {
                console.log(err);
            }

            for (const [key, value] of Object.entries(device.measurements)) {
                let target = document.getElementById('device-' + device.id + '-' + key);
                let entry = 0;

                if (key.startsWith('outlet')) {
                    if (value == 1) {
                        target.classList.remove('bi-toggle-off');
                        target.classList.add('bi-toggle-on');
                    } else {
                        target.classList.remove('bi-toggle-on');
                        target.classList.add('bi-toggle-off');
                    }
                } else {
                    if (['temperature','vpd'].indexOf(key) > -1) {
                        entry = value.toFixed(1);
                    } else {
                        entry = value.toFixed();
                    }

                    if (Object.keys(mySuffixes).indexOf(key) > -1) {
                        entry += mySuffixes[key];
                    }
                    target.innerHTML = entry;
                }
            }
        } catch(err) {
            console.log(err);
        }
    })
}


/** PRELOAD MODELS **/
Environment.loadList();
