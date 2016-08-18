"use strict";
module.exports = (options) => {
    options.app.get('/' , (req, res)=>{
        res.render('index.html')
    });
};
