var fs, exec, http;

var meteorRootDirectory = "/vega4/MIMIC2/scidb/pipeline/Step5_Viz/trunk/meteor_viz/";
var fileIODirectory = meteorRootDirectory + "file_io/";

var waveformIDFileName = "waveform_id.txt";

Meteor.startup(function() {
  fs = Npm.require("fs");
  http = Npm.require("http");
  exec = Npm.require("child_process").exec;
});


var waitForFileTimeout = 1000 * 10; // 10 seconds
var timeoutMessage = 'QUERY TIMED OUT';

function readFile(filePath) {
  var startTime = Date.now();
  while (true) {
    if (fs.existsSync(filePath)) {
      var fileContents = fs.readFileSync(filePath).toString();
      return fileContents.trim();
    } else {
      if (Date.now() - startTime > waitForFileTimeout) {
        return timeoutMessage;
      }
    }
  }
}

var waitForImageTimeout = 1000 * 30; // 30 seconds

function waitForImage(filePath) {
  var startTime = Date.now();
  while (true) {
    if (fs.existsSync(filePath)) {
      return true;
    } else {
      if (Date.now() - startTime > waitForImageTimeout) {
        return false;
      }
    }
  }
}

Meteor.methods({
  processMedicationAndPatientID: function(medicationName, patientID) {
    var execCommand = "cd " + meteorRootDirectory + "&& python submit_federated_query.py " + "&& sleep 30 && ./runPartHBVarianceCode";
    
    exec(execCommand,
      function(err, stdout, stderr) {
        console.log("ERR");
        console.log(err);
        console.log("STDOUT");
        console.log(stdout);
        console.log("STDERR");
        console.log(stderr);
      });

    var waveformID = readFile(fileIODirectory + waveformIDFileName);
    if (waveformID !== timeoutMessage) {
      fs.unlinkSync(fileIODirectory + waveformIDFileName);
    }
    return waveformID;
  },

  processWaveformImage: function(waveformID) {
    // call python function that will put image in file_io
    waveformImagePath = fileIODirectory + waveformID + ".png";
    if (waitForImage(waveformImagePath)) {
      return waveformID + ".png";
    } else {
      return "";
    }
  }
});

WebApp.connectHandlers.use(function(req, res, next) {
    var re = /^\/url_path\/(.*)$/.exec(req.url);
    if (re !== null) {   // Only handle URLs that start with /url_path/*
        var filePath = process.env.PWD + '/file_io/' + re[1];
        if (re[1] === '') {
          return;
        }
        var data = fs.readFileSync(filePath, data);
        res.writeHead(200, {
                'Content-Type': 'image'
            });
        res.write(data);
        res.end();
    } else {  // Other urls will have default behaviors
        next();
    }
});
