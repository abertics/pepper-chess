"use strict";
const net = require("net");
const host = "127.0.0.1";
const port = 9004;


var out;
var decodeOutput;
let decode = (options, callback) => {
    decodeOutput = JSON.parse(out) || out;
    // console.log(decodeOutput);
    callback({"pieces": decodeOutput["pieces"], "move": decodeOutput["move"]});
};



const client = net.connect({port: port}, () => {

    console.log('connected to server on port'+port+ '!');
    client.write('request');

});

client.on('data', (data) => {
    out = data;
    setTimeout(()=>{
        client.write('request');
    }, 1000)
});

client.on('end', () => {
    console.log('disconnected from server');
});




module.exports = {
    decode : decode,

};