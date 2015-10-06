var beep = (function () {
    var ctx = new(window.audioContext || window.webkitAudioContext);
    return function (duration, type, finishedCallback) {

        duration = +duration;

        // Only 0-4 are valid types.
        type = (type % 5) || 0;

        if (typeof finishedCallback != "function") {
            finishedCallback = function () {};
        }

        var osc = ctx.createOscillator();

        osc.type = type;

        osc.connect(ctx.destination);
        osc.noteOn(0);

        setTimeout(function () {
            osc.noteOff(0);
            finishedCallback();
        }, duration);

    };
})();

var muted = "false";
function saltymon() {
    var status = document.getElementById('betstatus');
    console.log("monitor ran: "+status.firstChild.nodeValue);
    if(status.firstChild.nodeValue == "Bets are OPEN!" && muted == "false") {
        beep(1000, 0);
        console.log("beeped");
    } else if (status.firstChild.nodeValue == "Bets are locked until the next match." && muted == "true") {
        muted = "false";
    }
    window.setTimeout(arguments.callee, 5000);
}

var page = document.getElementById('footer');
var btn = document.createElement("BUTTON");
btn.style.marginTop = "-60px";
btn.onclick = function() { muted = "true"; }
var t = document.createTextNode("Mute alert noise.");
btn.appendChild(t);
page.appendChild(btn);

saltymon()