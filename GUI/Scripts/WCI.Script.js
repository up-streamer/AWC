var Demo = false;
var pumpWarnAnimation = false; // For future use
var level;
var gndtklevel;
// Access 3rd gauge elements using DRY philosophy :)
function getID (obj) {
    return(document.getElementById(obj));
}

// send a request to the server to get the current levels and buttons state
function getControls() {
    // Json object expected
    /*   [{"timeOfReading":"08\/06\/2017 16:31:38", "level":"500", 
      "pump": "false", "pumpMode":"true", "gndtklevel":"2500","errorCode":"0"}] */

    // show the activity widget
    $("#waiting").show(1000);

    /* "http://123.456.789.000/getControls" */
    var hostName = window.location.hostName
    var jsonURL = "/getControls"
    //alert("jsonURL = " + jsonURL);

    $.getJSON(jsonURL, "", function (j) {
        // walk the responses and transfer it to objects. ErroCode Key is for future use
        // Level and gndtklevel range 0 to 100
        $("#onOffButton").val(j.pump);
        $("#manualAutoButton").val(j.pumpMode);
        level = j.level;
        gndtklevel = j.gndtklevel; 
        console.log("level = " + level);
        console.log("jSON = " + JSON.stringify(j));
        updateReadings();
        // hide the activity widget
        $("#waiting").hide(1000);
    });

}

function updateControls() {

    // show the activity widget
    $("#waiting").show(1000);

    //Send a request to the server, update commands to reflect buttons state.
    $.getJSON("/updateControls", {
        "Pump": $("#onOffButton").val(), 
        "PumpMode": $("#manualAutoButton").val()

        //Reset: resetController,                 // For future use
        // Restart: restartController,             // For future use

    }, function (j) {
        // hide the activity widget
        $("#waiting").hide(1000);
    });

}

// Control Panel

function updateReadings() {
    gauge.modify(getID('vertGauge1'), {values:[level,100]});
    gauge.modify(getID('vertGauge2'), {values:[gndtklevel,100]});
}
var barGaugePalette = ['#FF0000', '#FF6600', '#FF9900', '#669900', '#009933'];

var GaugeSettings = {
    width: '100%',
    height: '100%',
    max: 100,
    startAngle: 0,
    endAngle: 360,
    useGradient: true,

    title: {
        text: 'In-Ground Tank',
        subtitle: {
            text: 'Volume',
        },
    },
    values: [1],
    relativeInnerRadius: 0.6,
    tooltip: {
        visible: true,
        formatFunction: function (val) {
            return val * 100 + ' Liters';
        }
    },
    labels: {
        formatFunction: function (value) {
            return value + ' %';
        },
        precision: 0,
        indent: 0,
        connectorWidth: 1
    },

    formatFunction: function (value, index, color) {

        if (value < 20) {
            return barGaugePalette[0];
        }
        if (value < 40) {
            return barGaugePalette[1];
        }
        if (value < 60) {
            return barGaugePalette[2];
        }
        if (value < 80) {
            return barGaugePalette[3];
        }
        if (value <= 100) {
            return barGaugePalette[4];
        }
    },
};

// Buttons settings
var manualAutoButtonSettings = {
    onLabel: 'Auto',
    offLabel: 'Manual',
    height: 27,
    width: 120,
    checked: 'true',
};


function pumpAnimation() {
    if ($('#onOffButton').val() == 'ON') {
        if (pumpWarnAnimation) {
            $('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Warn.png").fadeTo(100, 1.00); });
        } else {
            $('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_On.png").fadeTo(500, 1.00); });
        };
    } else {
        $('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Off.png").fadeTo(100, 1.00); });
    };
};

// Manual/Auto button and on/off button logic
function controlPump() {
    $('#manualAutoButton').click(function () {
        if ($('#manualAutoButton').val() == 'Manual') {
            $('#manualAutoButton').val('Auto');
            $('#onOffButton').attr('disabled', true);
        } else {
            $('#manualAutoButton').val('Manual');
            $('#onOffButton').attr('disabled', false);
        };    /* alert("Clicked!");  */

/*         if ($('#manualAutoButton').val() == 'Auto') {
            $('#onOffButton').attr('disabled', 'disabled');
        } else {('#onOffButton').removeAttr('disabled')};
        } */
        buttonChange();
    });

    $('#onOffButton').click(function () {
        if ($('#onOffButton').val() == 'OFF') {
            $('#onOffButton').val('ON');
        } else {
            $('#onOffButton').val('OFF');
        };
        buttonChange();
    });
    /*     $('#manualAutoButton').mouseenter(function () {
            $('#manualAutoButton').on('click', manualAutoButtonChecked);
        });
    
        $('#manualAutoButton').mouseleave(function () {
            $('#manualAutoButton').off('click', manualAutoButtonChecked);
        });
    
        function manualAutoButtonChecked() {
            var checked = $("#manualAutoButton").jqxSwitchButton('checked');
            if (checked) {
                $('#onOffButton').jqxSwitchButton({ disabled: false });
            } else $('#onOffButton').jqxSwitchButton({ disabled: true });
        };
    
        $('#onOffButton').mouseenter(function () {
            $('#onOffButton').on('change', onOffButtonChange);
        });
    
        $('#onOffButton').mouseleave(function () {
            $('#onOffButton').off('change', onOffButtonChange);
        }); */

       function buttonChange() {
           pumpAnimation();
           updateControls();      
       }
};
function initWidgets() {

        gauge.add(getID('GroundTK'), {width:60, height:200, vertical:true, name: 'vertGauge1', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});

        gauge.add(getID('HeadTK'), {width:60, height:200, vertical:true, name: 'vertGauge2', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]}); 
};

// Simulate increasing values for Gauges
var increaseInterval;
function demoDisplay() {
    if ($("#onOffButton").val()) {
        i = 0;
        increaseInterval = setInterval(
            newValue
            , 1500);
    }
    else {
        i = 0;
        newValue();
        setTimeout(clearInterval(increaseInterval), 1000);
    }

    function newValue() {
        $("#levelGauge").val([i]);
        $("#GndTKLevelGauge").val([i]);
        $("#Gauge22").val([i]);
        gauge.modify(getID('vertGauge1'), {values:[i,100]});

        i = i + 10
        if (i > 100) { i = 0; }
    }
}

// For future use
function getControlsInterval() {
    setInterval(
        "getControls()"
    , 5000);
    };