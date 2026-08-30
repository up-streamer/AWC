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
    $("#waiting").show();
    /* "http://123.456.789.000/getControls" */
    var hostName = window.location.hostName
    var jsonURL = "/getControls"
    //alert("jsonURL = " + jsonURL);

    $.getJSON(jsonURL, "", function (j) {
        // walk the responses and transfer it to objects. ErroCode Key is for future use
        // headTklevel and gndtklevel range 0 to 100
        $("#onOffButton").val(j.pump);
        $("#manualAutoButton").val(j.pumpMode);
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

    // show the activity widget
    //$("#waiting").show();
    //Send a request to the server, update commands to reflect buttons state.
    $.getJSON("/updateControls", {
        "Pump": $("#onOffButton").val(), 
        "PumpMode": $("#manualAutoButton").val()

        //Reset: resetController,                 // For future use
        // Restart: restartController,             // For future use

    }, function (j) {
        // hide the activity widget
        //$("#waiting").fadeOut("slow");
    })
    .always(function() {
        txMode = false;
    });
}

// Control Panel
function updateReadings() {
    gauge.modify(getID('vertGauge1'), {values:[gndTkLevel,100]});
    gauge.modify(getID('vertGauge2'), {values:[headTklevel,100]});
    
    if ((headTkStatus != 'Ok') || (gndTkStatus != 'Ok')) {
        TKstatusFault = true;
    } else {
        TKstatusFault = false;
    }

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
    }

    if (unitsVol){
        $('#volumeGTK').text(gndTkVol + " Lts");
        $('#volumeHTK').text(headTkVol  + " Lts");
    } else {
        $('#volumeGTK').text(gndTkLevel  + " %");
        $('#volumeHTK').text(headTklevel  + " %");
    };

    pumpAnimation();
};

// Buttons settings
/* var manualAutoButtonSettings = {
    onLabel: 'Auto',
    offLabel: 'Manual',
    height: 27,
    width: 120,
    checked: 'true',
}; */

function pumpAnimation() {
    if ((onOffButton != $('#onOffButton').val()) || (TKstatusFault != TKfaultStatus)) {
        animateGaugeOnFault();
        animatePump();
        animateButton();
        onOffButton = $('#onOffButton').val(); 
    }

    function animateGaugeOnFault() {
		if(gndTkStatus != 'Ok'){
			gauge.modify(getID('vertGauge1'), {busy: true});
		} else {
			gauge.modify(getID('vertGauge1'), {busy: false});
		}
		
		if(headTkStatus != 'Ok'){
			gauge.modify(getID('vertGauge2'), {busy: true});
		} else {
			gauge.modify(getID('vertGauge2'), {busy: false});
		}
        TKfaultStatus = TKstatusFault;
	};

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

    $('#vertGauge1').click(function () {
        toggleUnits();
    });

    $('#vertGauge2').click(function () {
        toggleUnits();
    });

    function buttonChange() {
        pumpAnimation(); 
        txMode = true
    }

    function toggleUnits() {
        unitsVol = !unitsVol
        updateReadings();
    };
};

// Variable guage height 
var gaugeHeight

// Create a MediaQueryList object
var widthSmall = matchMedia("(max-width: 650px)")

function onWindowChange(widthSmall) {
  if (widthSmall.matches) { // If media query matches
    gaugeHeight = Math.floor(window.innerHeight / 5.64); //150
	//alert("Height small = " + gaugeHeight);
  } else {
    gaugeHeight = Math.floor(window.innerHeight / 2.11); //400
  }
	gauge.remove(getID('vertGauge1')); 
	gauge.remove(getID('vertGauge2')); 
	initGauges(gaugeHeight);
};

// Attach listener function on state changes
widthSmall.addEventListener("change", function() {
  onWindowChange(widthSmall);
});

// Init Widgets values
function initGauges (gaugeHeight) {
    gauge.add(getID('GroundTK'), {width:50, height:gaugeHeight, radius:0.5, vertical:true, name: 'vertGauge1', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});
    gauge.add(getID('HeadTK'), {width:50, height:gaugeHeight, vertical:true, name: 'vertGauge2', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});
};

function initWidgets() {
    statusFault = false
    TKstatusFault = true
    TKfaultStatus = false
    unitsVol = false
    onOffButton = 'OFF'
    pumpStatus = 'Ok'
    headTkStatus = 'Ok'
    gndTkStatus = 'Ok'
    flowSrStatus = 'Ok'
    $('#onOffButton').attr('disabled', true);
    var manualAutoButtonSettings = {
        onLabel: 'Auto',
        offLabel: 'Manual',
        height: 27,
        width: 120,
        checked: 'true',
    };

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