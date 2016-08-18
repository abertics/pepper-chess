"use strict";
const express = require("express");

var app = express();
app.use(express.static(__dirname+'/public'));

var options = {};
options.modelsPath = __dirname + "/server/models";
options.app = app;

require("./server/routes/chess")(options);
require("./server/routes/socketer")(options);






