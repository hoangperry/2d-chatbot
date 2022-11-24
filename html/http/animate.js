let images = [
    '/character/a.png',
    '/character/b.png',
    '/character/c.png',
    '/character/d.png',
    '/character/e.png',
    '/character/f.png',
    '/character/g.png',
    '/character/h.png',
    '/character/x.png',
];

let visemesAsset = {
    'A': '/character/a.png',
    'B': '/character/b.png',
    'C': '/character/c.png',
    'D': '/character/d.png',
    'E': '/character/e.png',
    'F': '/character/f.png',
    'G': '/character/g.png',
    'H': '/character/h.png',
    'X': '/character/x.png',
};

// Loads the images one at a time, then calls the callback function when all images
// have been loaded
function loadImages(images, index, callback) {
    if (index < images.length) {
        let img = new Image();
        img.src = images[index];
        images[index] = img;
        images[index].onload = function() {
            loadImages(images, ++index, callback);
        };
    } else {
        callback(images);
    }
}
window.onload = function() {
    loadImages(images, 0, (images) => {
        // Your slideshow code goes here. This is just example code
        // of adding the images to your document once they are all loaded
        images.forEach((item) => {
           document.querySelector('body').appendChild(item);
        });
    });
};

var visemesList = null, curPos = 0, curVisemes = 'X';


function sendMessage() {
    var session_id = $("#session_id").val()
    var messageText = $("#chatText").val()
    console.log("Client send: " + messageText);
    var settings = {
        "url": "/audio?text=" + messageText,
        "method": "POST",
        "headers": {
            "Content-Type": "text/plain"
        },
        "data": "{\"text\": \"" + messageText + "\"\n}",
        "crossDomain": true,
    };

    $.ajax(settings).done(function (response) {
        console.log(response);
        visemesList = response['visemes'];
        curPos = 0;
        $("#speechAudio").attr("src", "data:audio/wav;base64," + response['audio']);
    });
}
var crTime;
function setAnimation() {
    try{
//        var myaudio = document.getElementsByTagName("audio")[0];
        var crTime = document.getElementById("speechAudio").currentTime;
//        crTime = $("#speechAudio").data("jPlayer").status.currentTime;
        if (crTime > visemesList[curPos][0]){
            curPos += 1;
            if (curVisemes != visemesList[curPos][1]) {
                curVisemes = visemesList[curPos][1];
                $("#characterAnimated").attr("src", visemesAsset[curVisemes]);
            }
        }

        $("#PlayerTimer").html('Time: ' + parseFloat(crTime));
        console.log(crTime + ' : ' + curVisemes);
    } catch {
        if (curVisemes !== 'X'){
            console('BUG BUG BUG BUG');
            curVisemes = 'X';
            $("#characterAnimated").attr("src", visemesAsset['X']);
        }
    }
}
setInterval(setAnimation, 10);
//function updateTrackTime(track)  {
//    var currTime = Math.floor(track.currentTime).toString();
//    var duration = Math.floor(track.duration).toString();
//
//
//    if (isNaN(duration)){
//        console.log("0");
//    }
//    else{
//        console.log(track.currentTime);
//    }
//}