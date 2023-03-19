$( document ).ready(function() {
     $('#add_new_device').click(function() {
        $('#new_device_modal').modal('show')
    });
     $('.no-devices').click(function() {
        $('#new_device_modal').modal('show')
    });
    $('#open_save_cfg_modal').click(function() {
        $('#save_config_modal').modal('show')
    });
    $('#open_load_cfg_modal').click(function() {
        $('#load_config_modal').modal('show')
    });
})

