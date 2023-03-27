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
    $('#open_load_cfg_modal').click(async function() {
        $('#load_config_modal').modal('show');
        await render_configs_list();
    });
})

async function render_configs_list() {
    const data = await eel.get_configs()();
    if (data.error) {
        $('#list_config_errors').empty();
        $('#list_config_errors').append(data.msg);
        $('#list_config_errors').show();
        return
    }
    $('#configs_list').empty();
    $('#list_config_errors').empty();
    $('#list_config_errors').hide();

    for (let item of data.data) {
        $('<a/>')
            .addClass('list-group-item list-group-item-action cfg_item')
            .text(item)
            .appendTo($('#configs_list'));
    }

    $('.cfg_item').click(function() {
        $('.cfg_item').each((idx, el) => {
            $(el).removeClass('active');
        });
        $(this).addClass('active');
    })
}
