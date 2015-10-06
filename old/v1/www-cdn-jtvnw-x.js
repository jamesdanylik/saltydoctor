var betstate;
var x;
var p1n;
var p2n;
var p1te;
var p2te;
var p1to;
var p2to;
var alert;
var balance = Number($("#b").val()) || 0;
var u = $("#u").val();
var g = $("#g").val();
var sliderinterval = Number($("#i").val()) || 1;
var slidermax = Number($("#m").val()) || balance;
var _data;

$(document).ready(function () {
    
    $('input[type="submit"]').attr("disabled", "disabled");
    
    $("#light").click(function () {
        $( "#sbettors2" ).fadeOut( "fast", function() {
            
            if( !$("#sbettors1").hasClass( "lightsout" ) ) {
                $('.chat_embed:visible').slideUp(100);
                $("#sbettorswrapper").css("background-image","url(http://www.saltybet.com/images/textures/broken_noise.png)");
                $( "#sbettors1,#sbettors2,.sidebar-view" ).addClass( "lightsout" );
                var bettorsright = $('#sbettors2').detach();
                $('#chat-wrapper').append(bettorsright);
                $('#sbettors2').fadeIn("fast");
            } else {
                
                $("#sbettorswrapper").css("background-image","url(http://www.saltybet.com/images/textures/light/lightpaperfibers.png)");
                $( "#sbettors1,#sbettors2,.sidebar-view" ).removeClass( "lightsout" );
                var bettorsright = $('#sbettors2').detach();
                $('#sbettorswrapper').append(bettorsright);
                $('#sbettors2').fadeIn("fast");
                $('#chat-frame-stream').show();
                $('.chat_embed:visible').slideDown(100);
            }
          });
    });
    
    $(".button-purple").click(function () {
            interval = $(this).attr('id');
            if(Number($(this).val()) === 0) {
                $('#wager').val( Math.ceil((balance/10) * Number(interval.substr(8))));
            } else {
                $('#wager').val(Number($(this).val()));
            }
    });

});

var socket = io.connect("http://www-cdn-twitch.saltybet.com:8000");
socket.on("message", function (data) {
    try {
        $('input[type="submit"]').attr("disabled", "disabled");
        updateState();
    } catch (e) {
        console.log("invalid data");
        return;
    }
});

function updateState() {
    $.ajax({
        type: "get",
        url: "../state.json",
        contentType: "application/json; charset=utf-8",
        data: "",
        dataType: "json",
        cache: "false",
        timeout: 30000,
        success: function (data) {
            betstate = data.status;
            x = data.x;
            p1n = data.p1name;
            p2n = data.p2name;
            p1te = data.p1total;
            p2te = data.p2total;
            p1to = parseInt(p1te.replace(/,/g, ""));
            p2to = parseInt(p2te.replace(/,/g, ""));
            alert = data.alert;
            remaining = data.remaining;
            
            
            if((remaining.substr(-8) === "bracket!" || remaining.substr(11) === "FINAL ROUND") && !(remaining.substr(2) !== "16" && (betstate === "1" || betstate === "2"))) {
                $(".dollar").addClass("purpletext");
                if($("#tournament-note").length == 0) {
                    $("#balancewrapper").append('<span id="tournament-note">(Tournament Balance)</span>');
                }
            } else if($("#tournament-note").length) {
                $('#tournament-note').remove();
            }
            
            if(betstate === "open") {
                $('input[type="submit"]').removeAttr("disabled");
                if(u) {
                    if(alert === "Tournament mode start!") {
                            $.ajax({
                            type: "get",
                            url: "../ajax_tournament_start.php",
                            dataType: "html",
                            cache: "false",
                            success: function (data) { 
                                balance = Number(data); 
                                $("#balance").hide().html(addCommas(balance)).fadeIn("slow"); 
                                $("#wager").rules("add", {
                                    max: balance
                                });
                            }
                            });

                    } else if (alert === "Exhibition mode start!") {
                            $.ajax({
                            type: "get",
                            url: "../ajax_tournament_end.php",
                            dataType: "html",
                            cache: "false",
                            success: function (data) { 
                                balance = Number(data); 
                                $("#balance").hide().html(addCommas(balance)).fadeIn("slow"); 
                                $("#wager").rules("add", {
                                    max: balance
                                });
                            }
                            });
                        $(".dollar").removeClass("purpletext");
                        
                    }
                }

                $("#player1").val(p1n);
                $("#player2").val(p2n);
                if($("#betconfirm").length == 0) {
                    $("#odds,#lastbet").html("");
                }
                
                $("#wrapper").removeClass("locked").addClass("open");

                $("#betstatus").hide().html('Bets are OPEN!').fadeIn("slow");
                $("#sbettors1").hide().html('<span class="redtext"><strong>' + p1n + '</strong></span><div id="bettors1"></div>').fadeIn("slow");
                $("#sbettors2").hide().html('<span class="bluetext"><strong>' + p2n + '</strong></span><div id="bettors2"></div>').fadeIn("slow");
                
                if(balance > 0){
                    $("#wager").rules("add", {
                        max: balance
                    });
                }
  

                $("#header").css("border-top-color", "#4db044");
                $("#fightcard").css("border-top-color", "#4db044");
                $("#status").css("background", "#4db044");
                $("#status").css("border-top-color", "#4db044");
                $("#wager").css("border-color", "#4db044");
                $(".alert").css('display','none');
                $(".dynamic-view").fadeIn("fast");

            } else {
                $("#wrapper").removeClass("open").addClass("locked");

                if (!alert) {
                    $("#footer-alert").html(remaining);
                 } else {
                     $("#footer-alert").html(alert);
                 }

                if (betstate === "locked") {
                    $(".dynamic-view,label.error").fadeOut("fast");
                    $('input[type="submit"]').attr("disabled", "disabled");
                    $("#betstatus").hide().html("Bets are locked until the next match.").fadeIn("slow");
                    $("#header").css("border-top-color", "black");
                    $("#fightcard").css("border-top-color", "black");
                    $("#status").css("background", "black");
                    $("#status").css("border-top-color", "black");
                    $("#wager").css("border-color", "black");

                } else {

                    $("#wager").val("");

                    if (betstate === "1")
                    {
                        $("#betstatus").hide().html(p1n + " wins! Payouts to Team Red.").fadeIn("slow");
                        $("#header").css("border-top-color", "#D14836");
                        $("#fightcard").css("border-top-color", "#D14836");
                        $("#status").css("background", "#D14836");
                        $("#status").css("border-top-color", "#D14836");
                        $("#wager").css("border-color", "#D14836");
                    }else if(betstate === "2") {
                        $("#betstatus").hide().html(p2n + " wins! Payouts to Team Blue.").fadeIn("slow");
                        $("#header").css("border-top-color", "#349EFF");
                        $("#fightcard").css("border-top-color", "#349EFF");
                        $("#status").css("background", "#349EFF");
                        $("#status").css("border-top-color", "#349EFF");
                        $("#wager").css("border-color", "#349EFF");
                    }
                }
            }  
            if (x === 1) {
                updateData();
            } else if(g === "1") {
                updateStats();
            }
        }
    });
}

function updateData() {
    $.ajax({
        type: "get",
        url: "../zdata.json",
        contentType: "application/json; charset=utf-8",
        data: "",
        dataType: "json",
        cache: "false",
        timeout: 20000,
        success: function (data) {
            if (betstate === "locked") {
                
                var matchTotalDisplay;
                var p1odds = 1;
                var p2odds = 1;
                var oddsDisplay;
                if (p1to >= p2to) {
                        p1odds = Math.round((p1to / p2to) * 10) / 10;
                    } else {
                        p2odds = Math.round((p2to / p1to) * 10) / 10;
                    }
                oddsDisplay = ' <span class="redtext">' + p1odds + '</span>:<span class="bluetext">' + p2odds +'</span>';
                matchTotalDisplay = '<span class="redtext">' + p1n + ' </span> $' + p1te + '&nbsp;<span class="bluetext">&nbsp;' + p2n + " </span> $" + p2te; 
                $(".alert").fadeIn("slow");
                $("#odds").hide().html(matchTotalDisplay).fadeIn("slow");

                if (typeof data[u] != "undefined") {
                    lastWager = data[u]["w"];
                    lastPlayer = data[u]["p"];

                    payout = (data[u]["p"] == "1" ? ((lastWager / p1to) * p2to) : ((lastWager / p2to) * p1to));
                    payout = Math.ceil(payout);

                    (lastPlayer == "1" ? $("#lastbet").hide().html('<span class="redtext">$' + lastWager + "</span> &#8594;  " + '<span class="greentext">+$' + (payout || 0) + "</span> | " + oddsDisplay  ).fadeIn("slow") : $("#lastbet").hide().html('<span class="bluetext">$' + lastWager + '</span> &#8594;  '  + '<span class="greentext">+$' + (payout || 0) + "</span> | " + oddsDisplay).fadeIn("slow"));
                } else {
                    $("#lastbet").hide().html(oddsDisplay).fadeIn("slow");
                }
                    
                var bettors = [];
                var countp1 = 0;
                var countp2 = 0;
                var level;
                var mylevel;
                var levelimage;
                var wagerDisplay;
                
                for (var p in data) {
                    bettors[+p] = data[p];
                    if (data[p] != null) {
                        if (data[p]["w"] != null) {
                            if(bettors[p]["p"] == "1") {
                                countp1++;
                            } else if(bettors[p]["p"] == "2") {
                                countp2++;
                            }
                        }
                    }
                }
                bettors.sort(function (a, b) {
                    return parseFloat(b.w) - parseFloat(a.w);
                });
                
                $("#sbettors1").hide().html('<span class="redtext"><strong>' + p1n + '</strong> (' + countp1 + ')</span><div id="bettors1"></div>').fadeIn("slow");
                $("#sbettors2").hide().html('<span class="bluetext"><strong>' + p2n + '</strong> ('+ countp2 + ')</span><div id="bettors2"></div>').fadeIn("slow");

                $("#sbettorswrapper").hide();
                $.each(bettors, function (i, v) {
                    if (bettors[i] != null) {
                        
                        levelimage = '<span class="nolevelimage"></span>';
                        level = bettors[i]["r"];
                        
                        if (data[u] != null) {
                            if (data[u]["n"] == bettors[i]["n"]) {
                                mylevel = level;
                            }
                        }
                        
                        if (level > 0  && level.length <= 2) {
                            levelimage = '<img src="../images/ranksmall/rank' + level + '.png" class="levelimage">';
                        } else if (level.length > 2) {
                            levelimage = '<img src="http://www.gravatar.com/avatar/' + level + '?d=mm&s=25" class="levelimage">';
                        }
                        
                        if(parseInt(bettors[i]["w"]) >= 1000000) {
                            wagerDisplay = (bettors[i]["w"] / 1000000).toFixed(1) + 'M';
                        } else if(parseInt(bettors[i]["w"]) >= 1000) {
                            wagerDisplay = (bettors[i]["w"] / 1000).toFixed(1) + 'K';
                        } else {
                            wagerDisplay = bettors[i]["w"];
                        }
                            
                        if (bettors[i]["p"] == "1") {
                            $("#bettors1").append(
                                    '<p class="bettor-line">' + levelimage 
                                    + '<span ' + (bettors[i]["w"] === bettors[i]["b"] ? ' class="purpletext ' : ' class="greentext ') + 'wager-display">$' + wagerDisplay + '</span><span class="redtext"> | </span>' 
                                    + "<strong " + (bettors[i]["g"] == 1 ? 'class="goldtext"' : "") + ">" + bettors[i]["n"] + '</strong></p>');
                        } else if (bettors[i]["p"] == "2") {
                            $("#bettors2").append(
                                     '<p class="bettor-line">' + levelimage 
                                    + '<span ' + (bettors[i]["w"] === bettors[i]["b"] ? ' class="purpletext ' : ' class="greentext ') + 'wager-display">$' + wagerDisplay + '</span><span class="bluetext"> | </span>'
                                    + '<strong ' + (bettors[i]["g"] == 1 ? 'class="goldtext"' : "") + ">" + bettors[i]["n"] 
                                    + "</strong></p>" );
                        }
                    }
                });
                $("#sbettorswrapper").show();
            } else {
                if (typeof data[u] != "undefined") {
                    balance = Number(data[u]["b"]) || 0;
                    $("#b").val(balance);
                    $("#balance").hide().html(addCommas(balance)).fadeIn("slow");
                    if (mylevel > 0 && mylevel.length <= 2) {
                        $("#rank").html('<img src="../images/ranksmall/rank' + mylevel + '.png" class="levelimage">');
                    }
                    $("#wager").rules("add", {
                        max: balance
                    });
                }
            }
        }
    });
}

function updateStats() {
    $.ajax({
        type: "get",
        url: "../ajax_get_stats.php",
        data: "",
        dataType: "json",
        cache: "false",
        timeout: 30000,
        success: function (data) {
           p1name = data.p1name;
           p1totalmatches = data.p1totalmatches;
           p1winrate= data.p1winrate;
           p1tier = data.p1tier;
           p1life = data.p1life;
           p1meter = data.p1meter;
           p1palette = data.p1palette;
           p1author = data.p1author;
           
           p2name = data.p2name;
           p2totalmatches = data.p2totalmatches;
           p2winrate = data.p2winrate;
           p2tier = data.p2tier;
           p2life = data.p2life;
           p2meter = data.p2meter;
           p2palette = data.p2palette;
           p2author = data.p2author;
           
            $("#bettors1").append('<br/><p class="bettor-line"><span class="goldtext">Total matches </span>' + p1totalmatches + '</p>' 
            + '<p class="bettor-line"><span class="goldtext">Win rate </span>' + p1winrate + '%</p>'
            + '<p class="bettor-line"><span class="goldtext">Tier </span>' + p1tier + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Life </span>' + p1life + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Meter </span>' + p1meter + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Palette </span>' + p1palette + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Author </span>' + p1author + '</p>'
            );

            $("#bettors2").append('<br/><p class="bettor-line"><span class="goldtext">Total matches </span>' + p2totalmatches + '</p>' 
            + '<p class="bettor-line"><span class="goldtext">Win rate </span>' + p2winrate + '%</p>'
            + '<p class="bettor-line"><span class="goldtext">Tier </span>' + p2tier + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Life </span>' + p2life + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Meter </span>' + p2meter + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Palette </span>' + p2palette + '</p>'
            + '<p class="bettor-line"><span class="goldtext">Author </span>' + p2author + '</p>'
            );

        }
    });
}

$("input[type=submit]").click(function () {
    $("#lastbet").hide();
    var selectedPlayer = $(this).attr("name");
    $("#selectedplayer").val(selectedPlayer);
    if ($("#wager").val().length > 0 && Number($("#wager").val()) <= balance && isNaN(Number($("#wager").val())) == false) {
        if(selectedPlayer === 'player1'){
                $("#odds").hide().html('<span class="redtext">&larr;</span>').fadeIn("fast");
        }
        else if(selectedPlayer === 'player2'){
                $("#odds").hide().html('<span class="bluetext">&rarr;</span>').fadeIn("fast");
        }
    }
});

$(function () {
    $("form").bind("submit", function () {
        if (betstate === "locked") {
            alert("Bets are locked.");
        } else {
            if (isNaN(Number($("#wager").val())) == true) {
                alert("Please enter a number.");
            } else {
                if (Number($("#wager").val()) > balance) {
                    alert("You don't have enough Salty Bucks.");
                } else {
                    $.ajax({
                        type: "post",
                        url: "../ajax_place_bet.php",
                        data: $("form").serialize(),
                        success: function (data) {
                            if($('#wrapper').hasClass('open') && data.length > 0) {
                                $("#lastbet").hide().html('<span id="betconfirm" class="greentext">&#10003;</span>').fadeIn("slow");
                            }
                            $('input[type="submit"]').attr("disabled", "disabled");
                            setTimeout(function (data) {
                                $('input[type="submit"]').removeAttr("disabled");
                            }, 3000);
                        }
                    });
                    return false;
                }
            }
        }
    });
});

function addCommas(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}