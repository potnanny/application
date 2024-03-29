/** DEFAULTS **/
const KEYCHAIN_DEFAULT = {
    name: null,
    attributes: {} };


/** MODELS **/
var Keychain = {
    list: [],
    current: KEYCHAIN_DEFAULT,

    loadList: function() {
        let route = API_URI + "/keychains";
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
            Keychain.list = data.msg;
        }).catch(function(err) {
            console.log(err);
        })
    },
    load: function(id) {
        Keychain.current = KEYCHAIN_DEFAULT;
        for (let o of Keychain.list) {
            if (o.id == id) {
                Keychain.current = o;
                break;
            }
        }
    },
    loadName: function(name) {
        Keychain.current = KEYCHAIN_DEFAULT;
        for (let o of Keychain.list) {
            if (o.name == name) {
                Keychain.current = o;
                break;
            }
        }
    },
    save: function() {
        let method = "POST";
        let route = API_URI + "/keychains";

        if (Keychain.current.id) {
            method = "PATCH";
            route += "/" + Keychain.current.id
        }

        return fetch(route, {
            method: method,
            credentials: 'same-origin',
            headers: {
                "X-CSRF-Token": CSRF_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(Keychain.current)
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw "response was not ok";
            }
        }).then(function(data) {
            Keychain.current = data.msg;
            Keychain.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    },
    delete: function() {
        let route = API_URI + "/keychains/" + Keychain.current.id;
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
            Keychain.current = KEYCHAIN_DEFAULT;
            Keychain.loadList();
        }).catch(function(err) {
            console.log(err);
        })
    }
}

/** PRELOAD MODELS **/
setTimeout(function() { Keychain.loadList(); }, 300);
