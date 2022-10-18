$( document ).ready(function() {
    let panels = $('.main-panel');
    $('.panel-switcher').each(function() {
        let switcher = this;
        console.log(switcher.id);
        // console.log(this);
        // console.log(switcher);
        $(switcher).click(function() {
            console.log(switcher.id, " clicked");
            panels.each(function() {
                $(this).hide();
            })

            if (switcher.id === "panel_switch__deivces") {
                $('#panel-home').show()
            } else if (switcher.id === "panel_switch__continous_measure") {
                $('#panel-cm').show()
            } else if (switcher.id === "panel_switch__single_meas") {
                $('#panel-sm').show()
            } else if (switcher.id === "panel_switch__scan_meas") {
                $('#panel-scan').show()
            } else if (switcher.id === "panel_switch__log") {
                $('#panel-log').show()
            }
        })
    });
});