var activeModal = null;

const showModal = function(content) {
    if (activeModal == null) {
        activeModal = new bootstrap.Modal(document.getElementById('myModal'));
    }
    let body = document.getElementById('myModalBody');
    m.render(body, content);
    activeModal.toggle();
}


const hideModal = function() {
    try {
        activeModal.hide();
    } catch(err) {
        console.log(err);
    }
}
