$( document ).ready(function() {
    $('#clear_log').click(function() {
        $('#log').val('').change();
    })

    $('#log').change(function() {
        $('#log').scrollTop($('#log')[0].scrollHeight);
    })
})

eel.expose(push_el_to_log);
function push_el_to_log(data) {
    $('#log').append(data);

}