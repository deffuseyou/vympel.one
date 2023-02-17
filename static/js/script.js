
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/updater');

    //receive details from server
    socket.on('update', function(msg) {

        console.log(msg.balance);

        $('#squad_1').html((Math.round(msg.balance[0] * 100) / 100).toFixed(2).toString() + ' ₡');
        $('#squad_2').html((Math.round(msg.balance[1] * 100) / 100).toFixed(2).toString() + ' ₡');
        $('#squad_3').html((Math.round(msg.balance[2] * 100) / 100).toFixed(2).toString() + ' ₡');
        $('#squad_4').html((Math.round(msg.balance[3] * 100) / 100).toFixed(2).toString() + ' ₡');

        // $('#squad_5').html((Math.round(msg.balance[4] * 100) / 100).toFixed(2).toString() + ' ₡');
    });

});