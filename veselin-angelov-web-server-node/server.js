const net = require('net');
const fs = require('fs')
const path = require("path");
const { spawn } = require('child_process');

const CHUNK_SIZE = 100000;
const MAX_PROCESSES = 10;

const responseStatuses = {
    OK: {
        status: 'OK',
        code: 200,
    },
    NOT_FOUND: {
        status: 'Not Found',
        code: 404,
    },
    SERVER_ERROR: {
        status: 'Internal server error',
        code: 500,
    },
    NOT_IMPLEMENTED: {
        status: 'Not implemented',
        code: 501,
    }
};

const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.woff': 'application/font-woff',
    '.ttf': 'application/font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.otf': 'application/font-otf',
    '.wasm': 'application/wasm'
};

function createWebServer(requestHandler) {
    const server = net.createServer();
    server.on('connection', handleConnection);

    function handleConnection(socket) {
        // Subscribe to the readable event once so we can start calling .read()
        socket.on('error', function (e) {
            console.log(e);
        })
        socket.once('readable', function() {
            // Set up a buffer to hold the incoming data
            let reqBuffer = new Buffer('');
            // Set up a temporary buffer to read in chunks
            let buf;
            let reqHeader;
            while(true) {
                // Read data from the socket
                buf = socket.read();
                // Stop if there's no more data
                if (buf === null) break;

                // Concatenate existing request buffer with new data
                reqBuffer = Buffer.concat([reqBuffer, buf]);

                // Check if we've reached \r\n\r\n, indicating end of header
                let marker = reqBuffer.indexOf('\r\n\r\n')
                if (marker !== -1) {
                    // If we reached \r\n\r\n, there could be data after it. Take note.
                    let remaining = reqBuffer.slice(marker + 4);
                    // The header is everything we read, up to and not including \r\n\r\n
                    reqHeader = reqBuffer.slice(0, marker).toString();
                    // This pushes the extra data we read back to the socket's readable stream
                    socket.unshift(remaining);
                    break;
                }
            }

            const responseHeaders = {
                server: 'my-custom-server'
            };

            /* Request-related business */
            // Start parsing the header

            if (reqHeader === undefined) {
                return;
            }

            let reqHeaders = reqHeader.split('\r\n');
            const reqLine = reqHeaders.shift().split(' ');
            const reqUrl = reqLine[1].split('?');

            // Further lines are one header per line, build an object out of it.
            const headers = reqHeaders.reduce((acc, currentHeader) => {
                const [key, value] = currentHeader.split(':');
                return {
                    ...acc,
                    [key.trim().toLowerCase()]: value.trim()
                };
            }, {});

            // This object will be sent to the handleRequest callback.
            const request = {
                method: reqLine[0],
                url: reqUrl[0],
                args: reqUrl[1],
                httpVersion: reqLine[2].split('/')[1],
                headers,
                // The user of this web server can directly read from the socket to get the request body
                socket
            };

            /* Response-related business */
            // Initial values
            let headersSent = false;
            let isChunked = false;
            let status = responseStatuses.OK;

            function setHeader(key, value) {
                responseHeaders[key.toLowerCase()] = value;
            }
            function sendHeaders() {
                setHeader('date', new Date().toGMTString());
                socket.write(`HTTP/1.1 ${status.code} ${status.status}\r\n`);
                Object.keys(responseHeaders).forEach(headerKey => {
                    socket.write(`${headerKey}: ${responseHeaders[headerKey]}\r\n`);
                });
                socket.write('\r\n');
            }
            const response = {
                socket,
                sendHeaders,
                setHeader,
                setStatus(newStatus) {
                    status = newStatus;
                },
                write(chunk) {
                    if (!headersSent) {
                        // If there's no content-length header, then specify Transfer-Encoding chunked
                        if (!responseHeaders['content-length']) {
                            isChunked = true;
                            setHeader('transfer-encoding', 'chunked');
                        }
                        sendHeaders();
                    }
                    if (isChunked) {
                        const size = chunk.length.toString(16);
                        socket.write(`${size}\r\n`);
                        socket.write(chunk);
                        socket.write('\r\n');
                    }
                    else {
                        socket.write(chunk);
                    }
                },
                end(chunk) {
                    if (!headersSent) {
                        // We know the full length of the response, let's set it
                        if (!responseHeaders['content-length']) {
                            // Assume that chunk is a buffer, not a string!
                            setHeader('content-length', chunk ? chunk.length : 0);
                        }
                        sendHeaders();
                    }
                    if (isChunked) {
                        if (chunk) {
                            const size = (chunk.length).toString(16);
                            socket.write(`${size}\r\n`);
                            socket.write(chunk);
                            socket.write('\r\n');
                        }
                        socket.end('0\r\n\r\n');
                    }
                    else {
                        socket.end(chunk);
                    }
                },
            };

            // Send the request to the handler!
            requestHandler(request, response);
        });
    }

    return {
        listen: (port) => server.listen(port, 'localhost')
    };
}


let phpProcesses = [];

for (let i = 0; i < MAX_PROCESSES; i++) {
    phpProcesses.push({
        process: spawn('php', ['./cgi/mod_php.php']),
        request: null,
    });
}


phpProcesses.forEach(p => {
    let sent = false;
    p.process.stdout.on('data', data => {
        // console.log('2', p.request.res.socket.remoteAddress, p.request.res.socket.remotePort, p.request.id);
        if (!sent) {
            p.request.res.setStatus(responseStatuses.OK);
            p.request.res.setHeader('Content-type', mimeTypes['.html']);
            p.request.res.sendHeaders();
            sent = true;
        }
    });

    p.process.stdout.on('readable', () => {
        // console.log('r', p.request.id);
        let line;
        while (line = p.process.stdout.read()) {
            // console.log(line.toString());
            // console.log('3', p.request.res.socket.remoteAddress, p.request.res.socket.remotePort, p.request.id);
            if (line.toString().endsWith('END\n')) {
                line = line.toString().split('END\n')[0];
                p.request.res.socket.write(line);
                p.request.res.socket.end();
                processCount--;
                sent = false;
                p.request = null;
                phpProcesses.push(p);
            } else {
                p.request.res.socket.write(line);
            }
        }
    });

    p.process.stderr.on('data', data => {
        console.log(data.toString());
        p.request.res.setStatus(responseStatuses.SERVER_ERROR);
        p.request.res.end();
    });

    p.process.on('error', error => {
        console.log(error.toString());
        p.request.res.setStatus(responseStatuses.SERVER_ERROR);
        p.request.res.end();
    });

    p.process.on('close', code => {
        if (code !== 0) {
            console.log(`child process exited with code ${code}`);
        }
    });
});


function servePhpFiles(currentReq1) {
    let p = phpProcesses.shift();
    p.request = currentReq1;

    try {
        p.process.stdin.write(`${p.request.filePath}\n`);
        p.process.stdin.write(`${p.request.req.method}\n`);
        p.process.stdin.write(`${p.request.req.args}\n`);
        if (p.request.req.method === 'POST') {
            p.process.stdin.write(`${JSON.stringify(p.request.reqBody)}\n`);
        } else {
            p.process.stdin.write('undefined\n');
        }
        p.process.stdin.write('END\n');
    }
    catch (e) {
        console.log(e.toString());
    }
}


let requestQueue = [];
let processCount = 0;


setInterval(function () {
    // console.log(processCount, requestQueue.length);
    if (processCount < MAX_PROCESSES && requestQueue.length !== 0) {
        processCount++;
        try {
            let currentReq = requestQueue.shift();

            currentReq.filePath = '.' + currentReq.req.url;

            if (currentReq.filePath === './') {
                currentReq.filePath = './index.html';
            }

            let extname = String(path.extname(currentReq.filePath)).toLowerCase();

            if (currentReq.req.method === 'GET') {
                fs.access(`./cgi/${currentReq.filePath}`, fs.F_OK, error => {
                    if (error) {
                        currentReq.res.setHeader('Content-Type', mimeTypes[extname] || 'application/octet-stream');
                        fs.createReadStream(currentReq.filePath, {highWaterMark: CHUNK_SIZE})
                            .on('error', error => {
                                if (error.code === 'ENOENT') {
                                    currentReq.res.setStatus(responseStatuses.NOT_FOUND);
                                    currentReq.res.end();
                                    processCount--;
                                } else {
                                    currentReq.res.setStatus(responseStatuses.SERVER_ERROR);
                                    currentReq.res.end();
                                    processCount--;
                                }
                            })
                            .on('ready', chunk => {
                                currentReq.res.setStatus(responseStatuses.OK);
                                currentReq.res.sendHeaders();
                            })
                            .on('close', data => {
                                processCount--;
                            })
                            .pipe(currentReq.res.socket);
                    }
                    else {
                        servePhpFiles(currentReq);
                    }
                })
            }

            if (currentReq.req.method === 'POST') {
                fs.access(`./cgi/${currentReq.filePath}`, fs.F_OK, error => {
                    if (error) {
                        currentReq.res.setStatus(responseStatuses.NOT_IMPLEMENTED);
                        currentReq.res.end();
                        processCount--;
                    }
                    else {
                        let reqBuffer = new Buffer('');
                        let buf;
                        while (true) {
                            buf = currentReq.req.socket.read();
                            if (buf === null) break;

                            reqBuffer = Buffer.concat([reqBuffer, buf]);
                        }

                        currentReq.reqBody = JSON.parse(reqBuffer.toString());

                        servePhpFiles(currentReq);
                    }
                })
            }
        }
        catch (e) {
            console.log(e.toString());
            processCount--;
        }
    }
}, 1);


const webServer = createWebServer(async (req, res) => {
    console.log(`${new Date().toISOString()} - HTTP ${req.httpVersion} ${req.method} ${req.url}`);

    // console.log(res.socket.remoteAddress, res.socket.remotePort);

    requestQueue.push({req, res});
});

webServer.listen(3000);
