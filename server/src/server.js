const http = require("http");

port = 5000

http.createServer((req, res)=>{
    res.write("Hello")
    res.end()
}).listen(port)
