$(document).ready(function () {
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/updater');

    //receive details from server
    socket.on('update', function (msg) {

        console.log(msg.balance);

        $('#squad_1').html((Math.round(msg.balance[0] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_2').html((Math.round(msg.balance[1] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_3').html((Math.round(msg.balance[2] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_4').html((Math.round(msg.balance[3] * 100) / 100).toFixed(0).toString() + ' ⟠');
        // $('#squad_5').html((Math.round(msg.balance[4] * 100) / 100).toFixed(2).toString() + ' долек');

        $('#squad_1_e').html('1 отряд: ' + (Math.round(msg.balance[0] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_2_e').html('2 отряд: ' + (Math.round(msg.balance[1] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_3_e').html('3 отряд: ' + (Math.round(msg.balance[2] * 100) / 100).toFixed(0).toString() + ' ⟠');
        $('#squad_4_e').html('4 отряд: ' + (Math.round(msg.balance[3] * 100) / 100).toFixed(0).toString() + ' ⟠');

    });

});