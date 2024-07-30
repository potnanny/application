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

/** Functions for our Form **/
const addAttributeRow = function() {
    var parent = document.getElementById("attr-rows");
    var lastId = 0;
    if (parent.children.length > 0) {
        lastId = parseInt(parent.children[parent.children.length - 1].id.split('-')[1]);
    }

    var myDiv = document.createElement('tr');
	myDiv.id = "row-" + (lastId + 1);
	myDiv.className = 'attr-row';

    var html = '<td><input type="text" required class="attr-key form-control"></td>';
    html += '<td><input type="text" required class="attr-val form-control"></td>';
    html += '<td><a class="btn btn-sm" onclick="deleteAttributeRow(\'' + myDiv.id + '\')"><i class="bi bi-trash"></i></a></td>';

    myDiv.innerHTML = html;
	parent.appendChild(myDiv);
}

const deleteAttributeRow = function(id) {
    var parent = document.getElementById(id);
    parent.remove();
}

/** FORMS/MODALS **/
var keychainFormModal = function(id = undefined) {
    if (id) { Keychain.load(id); }

    var form = m("form", {
        onsubmit: function(e) {
            e.preventDefault();
            Keychain.current.attributes = {};
            var collection = document.getElementsByClassName('attr-row');
            for (const parent of collection) {
                var k = sanitizeInput(parent.querySelector('.attr-key').value);
                var v = sanitizeInput(parent.querySelector('.attr-val').value);
                Keychain.current.attributes[k] = v;
            }
            Keychain.save();
            hideModal();
            setTimeout(function() { window.location.reload(); }, 1500);
        }}, [
        m("label.form-label[for=name]", "Keychain Name"),
        m("input[type=text][required].form-control", {
            id: "name",
            value: Keychain.current.name,
            onchange: function(e) {
                Keychain.current.name = sanitizeInput(e.target.value);
            }}
        ),
        m("table.table.table-striped.mt-3", [
            m("thead", [
                m("tr", [
                    m("th", "key"),
                    m("th", "value"),
                    m("th",
                        m("a.btn", {onclick: function() { addAttributeRow(); }},
                            m("i.bi.bi-plus-circle")
                        )
                    )
                ])
            ]),
            m("tbody", {id: "attr-rows"}, Object.keys(Keychain.current.attributes).sort().map(function(k, i) {
                var rowid = "row-" + i;
                return m("tr.attr-row", {id: rowid}, [
                    m("td", m("input[type=text][required].form-control.attr-key", {value: k})),
                    m("td", m("input[type=text][required].form-control.attr-val", {value: Keychain.current.attributes[k]})),
                    m("td", m("a.btn.btn-sm", {onclick: function() { deleteAttributeRow(rowid) }},
                        m("i.bi.bi-trash")
                    ))
                ])
            }))
        ]),
        m("div.mt-4.row.row-cols-2", [
            m("div.col",
                m("button[type=submit].submit.btn.btn-primary.form-control", "Save")
            ),
            (Keychain.current.id) ? m("div.col",
                m("button.btn.btn-outline-danger.form-control", {
                    onclick: function(e) {
                        e.preventDefault();
                        if (confirm("Are you sure you want to delete this Keychain and all of its data?")) {
                            Keychain.delete();
                            hideModal();
                            setTimeout(function() { window.location.reload(); }, 1500);
                        }
                    }}, "Delete")) : null
        ])
    ]);

    showModal(form);
}

/** PRELOAD MODELS **/
setTimeout(function() { Keychain.loadList(); }, 300);
