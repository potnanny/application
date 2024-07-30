const API_URI = "/api/v1.0";

const dateFromISO = function(value) {
    let d = new Date(Date.parse(value));
    return d;
}

const localizeTimestamps = function() {
    let elements = document.getElementsByClassName('timestamp');
    for (let e of elements) {
        try {
            let d = dateFromISO(e.innerHTML);
            e.innerHTML = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        } catch (error) {
            console.log(error);
        }
    }
}

const sanitizeInput = function(unsafe, forAttribute) {
    const ESC_MAP = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    return unsafe.replace(forAttribute ? /[&<>'"]/g : /[&<>]/g, function(c) {
        return ESC_MAP[c];
    });
}
