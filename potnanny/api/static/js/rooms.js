/** DEFAULTS **/
const ROOM_DEFAULT = {
    name: null,
    notes: null };


/** MODELS **/
var Room = {
    list: [],
    current: ROOM_DEFAULT,

    loadList: function() {
        let route = API_URI + "/rooms";
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
            Room.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    load: function(id) {
        Room.current = ROOM_DEFAULT;
        for (let o of Room.list) {
            if (o.id == id) {
                Room.current = o;
                break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/rooms";

        if (Room.current.id) {
            method = "PATCH";
            route += "/" + Room.current.id
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(Room.current)
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Room.current = data.msg;
            Room.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/rooms/" + Room.current.id;
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
            Room.current = ROOM_DEFAULT;
            Room.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    }
}


var roomNameModal = function(id = undefined) {

    if (id) { Room.load(Number(id)); }

    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            hideModal();
            Room.save();
            setTimeout(function() { Room.loadList(); }, 250);
            setTimeout(function() { window.location.reload(); }, 500);
        }}, [
        m("input[type=text][required][placeholder=Room Name].form-control", {
            id: "roomname",
            value: Room.current.name,
            onchange: function(e) {
                Room.current.name = e.target.value;
            }
        }),
        m("button[type=submit].submit.btn.btn-primary.mt-2.float-right", "Save")
    ]);

    showModal(form)
}

var roomNotesModal = function(id = undefined) {
    if (id) { Room.load(Number(id)); }

    let form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            Room.current.notes = document.getElementById('roomnotes').value;
            hideModal();
            Room.save();
            Room.current = ROOM_DEFAULT;
            Room.loadList();
        }}, [
        m("textarea[rows=6][placeholder=Room Notes].form-control", {
            value: Room.current.notes,
            id: "roomnotes"}
        ),
        m("input[type=submit].btn.btn-primary.form-control.mt-3", {value: "Save"})
    ]);

    showModal(form);
}


/** PRELOAD MODELS **/
setTimeout(function() { Room.loadList(); }, 250);
