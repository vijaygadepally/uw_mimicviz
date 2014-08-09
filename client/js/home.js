Session.set("waveform_id", "");
Session.set("waveform_image_url", "");

Template.home.waveform_id = function() {
  return Session.get("waveform_id");
}

Template.home.waveform_image_url = function() {
  return Session.get("waveform_image_url");
}

Template.home.events = {
  "click div.query-button": function(event) {
    $("div.spin-loader").hide();
    $("div.waveform-image").hide();
    $("div.waveform-id-container").hide();

    var medicationName = $("input.input-medication-name").val().trim();
    var patientID = $("input.input-patient-id").val().trim();

    if ((medicationName === "") || (patientID === "")) {
      return;
    }

    $("div.spin-loader").show();

    Meteor.call("processMedicationAndPatientID", medicationName, patientID,
      function(error, result) {
        if (error) {
          console.log("[ERROR] Error on calling " +
            "processMedicationAndPatientID server method");
        } else {
          Session.set("waveform_id", result);
          $("div.waveform-id-container").fadeIn("slow");

          if (result === "QUERY TIMED OUT") {
            $("div.spin-loader").hide();
            return;
          }

          Meteor.call("processWaveformImage", result,
            function(error, result) {
              if (error) {
                console.log("[ERROR] Error on calling " +
                  "processWaveformImage server method");
              } else {
                Session.set("waveform_image_url", result);
                $("div.waveform-image").fadeIn("slow");
                $("div.spin-loader").hide();

                if (result === '') {
                  $("div.waveform-image").find("img").hide();
                  $("div.waveform-image").append("Request timed out.");
                }
              }
            });
        }
      });
  },
}
