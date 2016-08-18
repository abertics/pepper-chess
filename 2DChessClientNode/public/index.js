/**
 * Created by sdadian on 06/07/2016.
 */
var position ;
var socket = io.connect('http://localhost:3000');
setInterval(()=>{
    socket.emit('request');
}, 500);
socket.on('message', (message)=>{
    position = message;
    console.log(position);
    var board = ChessBoard('board', position);
});



