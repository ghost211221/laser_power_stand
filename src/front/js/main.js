$( document ).ready(function() {
    home_panel_handler.get_connections_translation_dict();
    home_panel_handler.render_devices();
    home_panel_handler.set_list_of_devices_models();
    home_panel_handler.set_list_of_devices_models_in_options();
    home_panel_handler.render_errors([]);

    $('#device_type').change(function() {
        home_panel_handler.set_list_of_devices_models();
    });

    home_panel_handler.chain_device_filling();

    $('#submit_new_device').click(async function() {
        let pass = await home_panel_handler.validate();
        home_panel_handler.add_new_device(
            pass,
            $('#device_name').val(),
            $('#device_type').val(),
            $('#device_model').val(),
            $('#device_connection_type').val(),
            $('#device_addr').val(),
        );
    })

    $('#update_device').click(function() {
        home_panel_handler.update_device();
    })


    $('#sm_laser').change(function() {

    })

    $(single_measure.wavelen_input).change(function() {single_measure.validate_wavelen()})
    $(single_measure.power_input).change(function() {single_measure.validate_power()})

});

eel.expose(set_device_status);
function set_device_status(device, status) {
    home_panel_handler.set_device_status(device, status);
}


let home_panel_handler = {
    no_device_submit_errors: null,
    added_devices: [],
    waiting_connection_devices: [],
    connections_translation_dict: [],
    switch_visual_mode: function() {
        if (this.added_devices.length === 0) {
            $('.has-devices').hide();
            $('.no-devices').show();
        } else {
            $('.has-devices').show();
            $('.no-devices').hide();
        }
    },

    update_device_connection_status: function(label, connected) {
        for (let device of this.added_devices) {
            if (device.label === label) {
                device.connected = connected;
            }
        }
    },

    clear_modal: function() {
        $('#device_name').val('');
        $('#device_type option').prop("selected", false);
        $('#device_model option').prop("selected", false);
        $('#device_connection_type option').prop("selected", false);
        $('#device_addr').val('');
        $('#add_new_device_alert').empty();
    },

    reinit_modal: function() {
        $('#device_model').prop("disabled", false);
        $('#device_connection_type').prop("disabled", false);
        $('#device_addr').prop("disabled", false);
    },

    get_connections_translation_dict: async function() {
        const res = await eel.e_get_connections_translations()();
        this.connections_translation_dict = res;
    },

    add_new_device: function(pass, device_name, device_type, device_model, device_connection_type, device_addr) {
        if (!pass) {
            // validation failed, do not add device
            return
        }

        // add to python
        eel.e_add_new_device(device_name, device_type, device_model, device_connection_type, device_addr)().then(response =>  {
            if (response.status === 'success') {
                this.clear_modal();
                this.reinit_modal();
                this.render_devices();
                $('#new_device_modal').modal('hide');
            } else if (response.status === 'fail') {
                alert(response.message);
            }
        });
    },

    update_device: function() {
        eel.e_update_device(
            $('#options__device_name').val(),
            $("#options__device_conntection").val(),
            $('#options__device_addr').val()
        )().then(response => {
            if (response.status === 'success') {
                this.render_devices();
                $('#device_modal').modal('hide');
            } else if (response.status === 'fail') {
                alert(response.message);
            }
        })
    },

    set_device_status: function(device_name, status) {
        let that = this;
        that.update_device_connection_status(device_name, status !== 'init')
        let lamp = $(`#lamp__${device_name}`);
        $(lamp).removeClass('lamp-init lamp-success lamp-error lamp-busy');
        let btn_selector = `#connect__${device_name}`;

        if (status === 'init') {
            $(lamp).addClass('lamp-init');
            $(btn_selector).text('Подключиться');
            $(btn_selector).prop('mode', 'connect');
            $(btn_selector).prop('disabled', false);
            that.waiting_connection_devices = that.waiting_connection_devices.push(device_name)
            
            single_measure.nest_emitters();
            single_measure.nest_trees();
        } else if (status === 'error') {
            $(lamp).addClass('lamp-error');
            let btn_selector = `#connect__${device_name}`;
            $(btn_selector).prop('disabled', false);
        } else if (status === 'processing') {
            $(lamp).addClass('lamp-busy')
        } else if (status === 'ready') {
            $(lamp).addClass('lamp-success')
            $(btn_selector).text('Отключиться');
            $(btn_selector).attr('mode', 'disconnect');
            $(btn_selector).prop('disabled', false);
            that.waiting_connection_devices = that.waiting_connection_devices.filter(function(e) { return e !== device_name })

            single_measure.nest_emitters();
            single_measure.nest_trees();
        }
    },

    render_device_card: function(device_name, device_type, device_model, device_connection_type, device_addr, device_status) {
        let that = this;
        let device_lamp_class = 'lamp-init';
        let button_mode = 'connect';
        let button_text = 'Подключиться';
        // restore device status
        if (device_status === 'ready') {
            device_lamp_class = 'lamp-success';
            button_mode = 'disconnect';
            button_text = 'Отключиться';
        } else if (device_status === 'error') {
            device_lamp_class = 'lamp-error';
        }

        $('.devices-card-group').append(`
            <div class="m-1 card text-black bg-secondary sm-3 device-card" style="max-width: 11rem; min-width: 11rem;" id="object__${device_name}">
                <div class="card-header" id="options__${device_name}">
                    <div class="d-flex justify-content-between">
                        ${device_name}
                        <div class="lamp ${device_lamp_class}" id="lamp__${device_name}"></div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="d-flex  flex-column justify-content-md-center">
                        <small class="form-text text-dark">${device_type}</small>
                        <small class="form-text text-dark">${device_model}</small>
                        <small class="form-text text-dark">${device_addr}</small>
                        <button class="btn btn-sm btn-light mt-2" id="connect__${device_name}" dev_name="${device_name}" mode="${button_mode}">${button_text}</button>
                        <button class="btn btn-sm btn-light mt-2" id="delete__${device_name}" dev_name="${device_name}">Удалить</button>
                    </div>
                </div>
            </div>
        `);

        // connect device on button press
        let btn_selector = `#connect__${device_name}`;
        $(btn_selector).click(function() {
            let dev_name = $(this).attr('dev_name');
            let mode = $(this).attr('mode');
            // that.waiting_connection_devices.append(dev_name);
            // $(this).prop('disabled', true);
            eel.e_connect_device(dev_name, mode)().then(response => {
                if (response.status === 'success') {
                    if (mode === 'connect') {

                        // $(btn_selector).text('Отключиться');
                        // $(btn_selector).attr('mode', 'disconnect');
                    } else if (mode === 'disconnect') {
                        // $(btn_selector).text('Подключиться');
                        // $(btn_selector).attr('mode', 'connect');
                    }
                } else if (response.status === 'fail') {
                    $(lamp).addClass('lamp-error');
                    $(btn_selector).text('Подключиться');
                    $(btn_selector).prop('mode', 'connect');
                    alert(response.message);
                }
            })
        });

        // enable read and modify for device
        let selector = `#options__${device_name}`;
        $(selector).click(function() {
            $('#device_modal').modal('show');
            eel.e_get_device_info(this.id.split('__')[1])().then(device => {
                $('#options__device_name').val(device.device_name)
                let type = null;
                for (let connection_tup of that.connections_translation_dict) {
                    if (connection_tup.includes(device.device_connection_type)) {
                        type = connection_tup[2];
                    }
                }
                $("#options__device_type").val(device.device_type).change();
                $("#options__device_model").val(device.device_model).change();
                $("#options__device_conntection").val(type).change();
                $('#options__device_addr').val(device.device_addr)
            });
        })

        // delete device
        let del_selector = `#delete__${device_name}`;
        $(del_selector).click(function() {
            let device_name = $(this).attr('dev_name');
            eel.e_delete_device(device_name)().then(response => {
                if (response.status === 'success') {
                    that.render_devices();
                } else if (response.status === 'fail') {
                    alert(response.msg);
                }
            })
        })


    },

    render_add_device_widget: function() {
        $('.devices-card-group').append(`
            <div class="m-1 card text-black bg-secondary sm-3 device-card" style="max-width: 11rem; min-width: 11rem;" id="add_new_device">
                <div class="card-body">
                    <div class="d-flex  flex-column justify-content-md-center">
                    <img src="../img/172525_plus_icon.svg" alt="">
                    </div>
                </div>
            </div>
        `);
        $('#add_new_device').click(function() {
            $('#new_device_modal').modal('show')
        });
    },

    render_devices: function() {
        $('.devices-card-group').empty()
        eel.e_get_added_devices()().then(response => {
            this.added_devices = response;
            this.switch_visual_mode();

            if (response.length !== 0) {
                for (let device of this.added_devices) {
                    this.render_device_card(device.label, device.type, device.model, device.connection_type, device.addr, device.status);
                }
                this.render_add_device_widget();
            }
            // nest trees and emitters selects
            single_measure.nest_emitters();
            single_measure.nest_trees();
        });
    },

    set_list_of_devices_models: function() {
        let group = $('#device_type').val();
        // clean models select and add none option
        const select = $('#device_model')
        $(select).children().remove();
        $(select).append(`<option value="" selected></option>`);

        eel.e_get_devices_models_list(group)().then((response) => {
            for (let item of response) {
                $(select).append(`<option value="${item}">${item}</option>`);
            }
        });
    },

    set_list_of_devices_models_in_options: function() {
        const select = $('#options__device_model')
        $(select).children().remove();
        $(select).append(`<option value="" selected></option>`);

        eel.e_get_devices_models_list('')().then((response) => {
            for (let item of response) {
                $(select).append(`<option value="${item}">${item}</option>`);
            }
        });
    },

    chain_device_filling: function() {
        $('#device_type').change(function() {
            if ($('#device_type').val() === '') {
                $('#device_model').prop("disabled", true);
                $('#device_connection_type').prop("disabled", true);
                $('#device_name').attr("disabled", "disabled");
            } else {
                $('#device_model').prop("disabled", false);
            }
        })

        $('#device_model').change(function() {
            if ($('#device_model').val() === '') {
                $('#device_connection_type').prop("disabled", true);
                $('#device_name').attr("disabled", "disabled");
            } else {
                $('#device_connection_type').prop("disabled", false);
            }
        })

        $('#device_connection_type').change(function() {
            if ($('#device_connection_type').val() === '') {
                $('#device_addr').prop("disabled", true);
            } else {
                $('#device_addr').prop("disabled", false);
            }
        })
    },

    render_errors: function(messages) {
        if (messages.length === 0) {
            $('#add_new_device_alert').hide();
            $('#add_new_device_alert').empty()
        } else {
            $('#add_new_device_alert').show();
            for (let message of messages) {
                $('#add_new_device_alert').append(`${message}<br>`)
            }
        }
    },

    validate: async function() {
        this.render_errors([]);
        let messages = [];
        let label = $('#device_name').val();

        if (label === '') {
            messages.push('Не указана метка прибора')
        }

        if ($('#device_type').val() === '') {
            messages.push('Не выбран тип прибора')
        }

        if ($('#device_model').val() === '') {
            messages.push('Не выбрана модель прибора')
        }

        if ($('#device_connection_type').val() === '') {
            messages.push('Не выбран протокол связи с прибором')
        }

        if ($('#device_addr').val() === '') {
            messages.push('Не указан адрес/порт для связи с прибором')
        }


        // check that lable in unique
        const labels = await eel.e_get_devices_labels_list()()
        if (labels.includes(label)) {
            messages.push('Прибор с такой меткой уже существует')
        }

        this.render_errors(messages);
        return messages.length === 0;
    },
}

class Measure {

    constructor() {
        this.emitter = null
        this.meters = []
        this.analysis_name = null
        this.wavelen = null
        this.wavelen_min = 1527.6
        this.wavelen_max = 1568.6
        this.power = null
        this.power_min = 7.58
        this.power_max = 56.23

        this.emitter_select = null
        this.metters_tree = null
        this.tree_data = []

        this.wavelen_input = null
        this.wavelen_alert = null
        this.wavelen_start_input = null
        this.wavelen_stop_input = null
        this.power_input = null
        this.power_alert = null
    }

    validate_wavelen() {
        let val = $(this.wavelen_input).val();
        if (val < this.wavelen_min || val > this.wavelen_max) {
            $(this.wavelen_alert).show();
            $(this.wavelen_alert).append('Указана недопустимая длина волны')
        } else {            
            $(this.wavelen_alert).hide();
            $(this.wavelen_alert).empty()
        }
    }

    validate_power() {
        let val = $(this.power_input).val();
        if (val < this.power_min || val > this.power_max) {
            $(this.power_alert).show();
            $(this.power_alert).append('Указана недопустимая мощность')
        } else {            
            $(this.power_alert).hide();
            $(this.power_alert).empty()
        }
    }

    nest_emitters() {
        $(this.emitter_select).empty()
        for (let emitter of home_panel_handler.added_devices) {
            if (!emitter.connected || emitter.type !== 'laser') {
                continue
            }
            let option = $('<option>', {value: `${emitter.label}`, text:`${emitter.label}`})
            if (this.emitter !== null && this.emitter !== '') {
                option.prop("selected", "selected")
            }
            $(this.emitter_select).append($(option))
        }
    }

    nest_trees() {
        this.tree_data = [];
        for (let device of home_panel_handler.added_devices) {
            if (device.type !== 'power_meter' || !device.connected) {
                continue
            }
            let children = [];
            for (let i = 1; i <= device.chanels; i++) {
                children.push({
                    'id': `device__${device.label}__ch__${i-1}`,
                    'text': `Канал ${i}`
                })
            }
            let subdata = {
                'id': `device__${device.label}`,
                'text' : device.label,
                'state' : {
                    'opened' : true,
                },
                'children' : children
            }
            this.tree_data.push(subdata)
        }

        // $(this.metters_tree).data('jstree', false).empty().jstree(data);
        $(this.metters_tree).jstree(true).settings.core.data = this.tree_data;
        $(this.metters_tree).jstree(true).refresh();
    }

    set_meters(labels) {
        this.meters = labels;
        eel.set_meters(this.analysis_name, this.meters)()
    }

    set_emitter(label) {
        this.emitter = label;
        eel.set_meters(this.analysis_name, this.emitter)()
    }

    set_wavelen(wavelen) {
        this.wavelen = wavelen;
        eel.set_meters(this.analysis_name, this.wavelen)()
    }

    set_wavelen_range(wavelen_min, wavelen_max) {
        this.wavelen_min = wavelen_min;
        this.wavelen_max = wavelen_max;
        eel.set_meters(this.analysis_name, this.wavelen_min, this.wavelen_max)()
    }

    set_power(power) {
        this.power = power;
        eel.set_power(this.analysis_name, this.power)()
    }

    clear_traces() {
        eel.clear_traces(this.analysis_name)()
    }

    run_analysis() {
        eel.run_analysis(this.analysis_name)()
    }

    stop_analysis() {
        eel.stop_analysis(this.analysis_name)()
    }
}

class SingleMeasure extends Measure {

    constructor() {
      super();
      this.analysis_name = 'single_meas';
      this.emitter_select = '#sm_laser'
      this.metters_tree = '#jstree_sm'
      this.wavelen_input = '#sm_wavelen'
      this.wavelen_alert = '#sm_wavelen_alert'
      this.power_input = '#sm_power'
      this.power_alert = '#sm_power_alert'
    }

  }

class ContMeasure extends Measure {

    constructor() {
      super();
      this.analysis_name = 'cont_meas';
      this.emitter_select = '#cm_laser'
    }

  }

class ScanMeasure extends Measure {

    constructor() {
      super();
      this.analysis_name = 'scan_meas';
      this.emitter_select = '#scm_laser'
    }

  }

  const single_measure = new SingleMeasure();