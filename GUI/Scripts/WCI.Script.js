// Access 3rd gauge elements using DRY philosophy :)
function getID (obj) {
    return(document.getElementById(obj));
}

// send a request to the server to get the current levels and buttons state
function getControls() {
    // show the activity widget
    $("#waiting").show();

    $.getJSON("/getControls", "", function (j) {
        // walk the responses and transfer it to objects.
        pump = j.pump;
        pumpMode = j.pumpMode;
        pumpStatus = j.pumpStatus;
        headTklevel = j.headTklevel;
        headTkVol = j.headTkVol;
        headTkStatus = j.headTkStatus;
        gndTkLevel = j.gndTkLevel;
        gndTkVol = j.gndTkVol;
        gndTkStatus = j.gndTkStatus;
        flowSrStatus = j.flowSrStatus; 
        console.log("jSON = " + JSON.stringify(j));
        updateReadings();
        // hide the activity widget
        $("#waiting").fadeOut("slow");
    });
}

function updateControls() {
    $.getJSON("/updateControls", {
        "Pump": $("#onOffButton").val(), 
        "PumpMode": $("#manualAutoButton").val()

        //Reset: resetController,                 // For future use
        // Restart: restartController,             // For future use

    })
    .always(function() {
        txMode = false;
    });
}

// Control Panel
function updateReadings() {
    if (!txMode){
        $("#onOffButton").val(pump);
        $("#manualAutoButton").val(pumpMode);
    }

    gauge.modify(getID('vertGauge1'), {values:[gndTkLevel,100]});
    gauge.modify(getID('vertGauge2'), {values:[headTklevel,100]});

    if (unitsVol){
        $('#volumeGTK').text(gndTkVol + " Lts");
        $('#volumeHTK').text(headTkVol  + " Lts");
    } else {
        $('#volumeGTK').text(gndTkLevel  + " %");
        $('#volumeHTK').text(headTklevel  + " %");
    };

    animateGaugeOnFault();

    if ((pumpStatus != 'Ok') || (headTkStatus != 'Ok') || (gndTkStatus != 'Ok') || (flowSrStatus != 'Ok')) {
		statusFault = true;
        $("#statustext").hide();
		$("#statustext").empty();
		$("#statustext").append("Bomba: " + pumpStatus + '<br/>');
		$("#statustext").append("Caixa: " + headTkStatus + '<br/>');
		$("#statustext").append("Cisterna: " + gndTkStatus + '<br/>');
        $("#statustext").append("Fluxo: " + flowSrStatus);
		$("#statustext").fadeIn("slow");
    } else {
        statusFault = false;
		$("#statustext").fadeOut("slow");
		$("#statustext").empty();
        $("#statustext").append("Ok");
        $("#statustext").fadeIn("slow");
    }

    pumpAnimation();
};

function animateGaugeOnFault() {
    if (gndTkStatus != 'Ok') {
        if (!vertGauge1Busy) {
            gauge.modify(getID('vertGauge1'), { busy: true });
            vertGauge1Busy = true;
        }
    } else {
        if (vertGauge1Busy) {
            gauge.modify(getID('vertGauge1'), { busy: false });
            vertGauge1Busy = false;
        }
    };

    if (headTkStatus != 'Ok') {
        if (!vertGauge2Busy) {
            gauge.modify(getID('vertGauge2'), { busy: true });
            vertGauge2Busy = true;
        }
    } else {
        if (vertGauge2Busy) {
            gauge.modify(getID('vertGauge2'), { busy: false });
            vertGauge2Busy = false;
        }
    };
};

function pumpAnimation() {
    if (onOffButton != $('#onOffButton').val()) {
        animatePump();
        animateButton();
        onOffButton = $('#onOffButton').val(); 
    }

    function animatePump() {
        if ($('#onOffButton').val() == 'ON') {
			if (statusFault) {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Warn.png").fadeTo(500, 1.00); });
			} else {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_On.png").fadeTo(500, 1.00); });
			}
        } else {
            $('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Off.png").fadeTo(100, 1.00); });
        };
    };

    function animateButton() {
        if($("#manualAutoButton").val() == 'Manual'){
            $("#onOffButton").attr('disabled', false);
        } else {
            $("#onOffButton").attr('disabled', true);
        }
    };
};

// Manual/Auto button and on/off button logic
function controlPump() {
    $('#pump').click(function () {
		if(($('#manualAutoButton').val() == 'Auto') && ($('#onOffButton').val() == 'OFF')){
			$("#manualAutoButton").hide();
			$("#manualAutoButton").val("Completar");
			$("#onOffButton").attr('disabled', false);
			$("#manualAutoButton").fadeIn("slow");
        } else if ($('#manualAutoButton').val() == 'Completar') {
            $("#manualAutoButton").val("Auto");
            $('#onOffButton').attr('disabled', true);
		};

        buttonChange();
	});

    $('#manualAutoButton').click(function () {
        if ($('#manualAutoButton').val() == 'Manual') {
            $('#manualAutoButton').val('Auto');
            $('#onOffButton').val('OFF');
            $('#onOffButton').attr('disabled', true);
        } else if ($('#manualAutoButton').val() == 'Auto'){
            $('#manualAutoButton').val('Manual');
            $('#onOffButton').attr('disabled', false);
            $('#onOffButton').val('OFF');
        };    /* alert("Clicked!");  */

        buttonChange();
    });

    $('#onOffButton').click(function () {
        if (($('#onOffButton').val() == 'OFF')) {
            $('#onOffButton').val('ON');
            if ($('#manualAutoButton').val() == 'Completar'){
                $('#onOffButton').attr('disabled', true);}
        } else {
            $('#onOffButton').val('OFF');
        };

        buttonChange();
    });

    function buttonChange() {
        pumpAnimation(); 
        txMode = true
    };
};

function controlUnits(){
    $('#vertGauge1').click(function () {
        toggleUnits();
    });

    $('#vertGauge2').click(function () {
        toggleUnits();
    });

    function toggleUnits() {
        unitsVol = !unitsVol
        updateReadings();
    };
};

// Variable guage height 
var gaugeHeight

// Create a MediaQueryList object
var widthSmall = matchMedia("(max-width: 650px)")

function onWindowChange() {
    gaugeHeight = Math.floor(window.innerHeight / 1.87); //450
	gauge.remove(getID('vertGauge1')); 
	gauge.remove(getID('vertGauge2')); 
	initGauges(gaugeHeight);
    // To enable again unit togle units
    controlUnits(); 
    // To enable again animation on fault
    vertGauge1Busy = false;
    vertGauge2Busy = false;
    animateGaugeOnFault()
};

// Attach listener function on state changes
widthSmall.addEventListener("change", function() {
  onWindowChange();
});

// Init Widgets values
function initGauges (gaugeHeight) {
    gauge.add(getID('GroundTK'), {width:50, height:gaugeHeight, radius:0.5, vertical:true, name: 'vertGauge1', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});
    gauge.add(getID('HeadTK'), {width:50, height:gaugeHeight, vertical:true, name: 'vertGauge2', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});
};

function initWidgets() {
    statusFault = false
    vertGauge1Busy = false
    vertGauge2Busy = false
    unitsVol = false
    pump = 'OFF'
    pumpMode = 'Auto'
    pumpStatus = 'Ok'
    headTkStatus = 'Ok'
    gndTkStatus = 'Ok'
    flowSrStatus = 'Ok'
    $('#onOffButton').attr('disabled', true);
	txMode = false
};

function txRxMode() {
     if (txMode){
        updateControls()
      } else {
        getControls()
      }
};

// Set sample interval
function getControlsInterval() {
    setInterval(
        'txRxMode()'
    , 2000);
    };