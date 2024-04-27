statusFault = false
faultstatus = false
unitsVol = false
onOffButton = "OFF"

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
        console.log("jSON = " + JSON.stringify(j));
        updateReadings();
        // hide the activity widget
        $("#waiting").fadeOut("slow");
    });
}

function updateControls() {

    // show the activity widget
    $("#waiting").show();
    //updateReadings();
    //Send a request to the server, update commands to reflect buttons state.
    $.getJSON("/updateControls", {
        "Pump": $("#onOffButton").val(), 
        "PumpMode": $("#manualAutoButton").val()

        //Reset: resetController,                 // For future use
        // Restart: restartController,             // For future use

    }, function (j) {
        // hide the activity widget
        $("#waiting").fadeOut("slow");
    });
}

// Control Panel
function updateReadings() {
    gauge.modify(getID('vertGauge1'), {values:[gndTkLevel,100]});
    gauge.modify(getID('vertGauge2'), {values:[headTklevel,100]});

    if ((pumpStatus != 'Ok') || (headTkStatus != 'Ok') || (gndTkStatus != 'Ok')) {
        statusFault = true;
		$("#statustext").hide();
		$("#statustext").empty();
		$("#statustext").append("Bomba: " + pumpStatus + '<br/>');
		$("#statustext").append("Caixa: " + headTkStatus + '<br/>');
		$("#statustext").append("Cisterna: " + gndTkStatus);
		 //alert("#statustext updated!"); 
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
var manualAutoButtonSettings = {
    onLabel: 'Auto',
    offLabel: 'Manual',
    height: 27,
    width: 120,
    checked: 'true',
};

function pumpAnimation() {
    if ((onOffButton != $('#onOffButton').val()) || (statusFault == !faultstatus)) {
        //borderSet();
        animatePump();
        onOffButton = $('#onOffButton').val();
        faultstatus = statusFault;
    }

    function borderSet() {
        if(gndTkStatus != 'Ok'){
            $('#groundtkdiv').addClass('alarmBorder');
        } else {
            $('#groundtkdiv').removeClass('alarmBorder');
        }
    
        if(headTkStatus != 'Ok'){
            $('#headtkdiv').addClass('alarmBorder');
        } else {
            $('#headtkdiv').removeClass('alarmBorder');
        }
    }
	// Border test
	//$('#groundtkdiv').addClass('alarmBorder');
    //$('#headtkdiv').addClass('alarmBorder');
	//$('#volumeGTK').addClass('alarmBorder');
	//$('#pumpdiv').addClass('alarmBorder');

    function animatePump() {
        if ($('#onOffButton').val() == 'ON') {
			if (statusFault) {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Warn.png").fadeTo(500, 1.00); });
			} else {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_On.png").fadeTo(500, 1.00); });
			}				
        } else {
			if (statusFault && ($("#manualAutoButton").val() == "Auto")) {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Warn.png").fadeTo(500, 1.00); });
			} else {
				$('#pump').fadeTo(100, 0.3, function () { $(this).attr("src", "Content/images/pumpRound_Off.png").fadeTo(100, 1.00); });
			}			
        };
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

    $('#vertGauge1').click(function () {
        toggleUnits();
    });

    $('#vertGauge2').click(function () {
        toggleUnits();
    });

    function buttonChange() {
        pumpAnimation();
        updateControls();
    }
    
    function toggleUnits() {
        unitsVol = !unitsVol
        updateReadings();
        //alert("Units toggled! Units = " + unitsVol ); 
    };
};
function initWidgets() {
    gauge.add(getID('GroundTK'), {width:60, height:200, vertical:true, name: 'vertGauge1', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]});
    gauge.add(getID('HeadTK'), {width:60, height:200, vertical:true, name: 'vertGauge2', limit: true, gradient: true, scale: 10, colors:['#ff0000','#00ff00'], values:[10,100]}); 
};


// Set sample interval
function getControlsInterval() {
    setInterval(
        'getControls()'
    , 2000);
    };