const toggleOutlet = function(deviceId, outletName) {

    let pk = parseInt(deviceId);
    let outlet = parseInt(outletName.split('_')[1]);
    let state = 0;

    let e = document.getElementById("device-" + pk + "-" + outletName);
    if (e.classList.contains("bi-toggle-on")) {
        state = 0;
        Device.switchDevice(pk, outlet, state);
        e.classList.remove("bi-toggle-on");
        e.classList.add("bi-toggle-off");
    } else {
        state = 1;
        Device.switchDevice(pk, outlet, state);
        e.classList.remove("bi-toggle-off");
        e.classList.add("bi-toggle-on");
    }
    RoomEnvironment.current.devices.map(function(d) {
        if (d.id == pk) {
            try {
                d.measurements[outletName] = state;
            } catch(err) {
                console.log(err);
            }
        }
    })
}
