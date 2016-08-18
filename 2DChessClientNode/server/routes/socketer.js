"use strict";
const http = require("http");
const sock = require("socket.io");


const express = require('express');

var portVR = 3003;
var app = express();
var pose = JSON.parse('{"piece":1 , "x":5 , "y":2}');
var dico = JSON.parse('{"a":1 , "b":2 , "c":3,"d":4 , "e":5 , "f":6, "g":7, "h":8}');

module.exports = (options) => {

    let boardState = require(options.modelsPath + "/boardState");
    // var findMove = require(options.modelsPath+'/findMove')();
    const socketerPort = 3000;
    var proxy= http.createServer(options.app);
    var io = sock.listen(proxy);
    var current_dispo = [];
    var current_dispo_VR = [];

    // findMove.init();


    io.sockets.on('connection', (socket)=>{
        socket.on('request', ()=>{
            boardState.decode(options, (out)=>{
                current_dispo = out;
            });
            // console.log(current_dispo);
            // var move = findMove.isMove(current_dispo);
            // console.log("MOVE: "+move);
            console.log(current_dispo["move"]);
            socket.send(current_dispo["pieces"]);

        });
        socket.send(current_dispo);
    });

    proxy.listen(socketerPort, ()=>{
        console.log('listening on port : ' + socketerPort);
    });


    app.post("/", (req,res) => {

        boardState.decode(options, (out)=>{
            current_dispo_VR = out;
        });


        if (current_dispo_VR[2]) {
            pose.x= dico[current_dispo_VR[2][0]];
            pose.y=current_dispo_VR[2][1];

        }
        res.send(pose);



    });

    app.listen(portVR);

};

