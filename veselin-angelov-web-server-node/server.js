const net = require('net');
const fs = require('fs')
const path = require("path");
const { spawn } = require('child_process');

const CHUNK_SIZE = 100000;

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

// let phpProcesses = 0;

const webServer = createWebServer(async (req, res) => {
    console.log(`${new Date().toISOString()} - HTTP ${req.httpVersion} ${req.method} ${req.url}`);

    let filePath = '.' + req.url;

    if (filePath === './') {
        filePath = './index.html';
    }

    let extname = String(path.extname(filePath)).toLowerCase();

    if (req.method === 'GET') {
        if (extname === '.php') {
            fs.access(`./cgi/${filePath}`, fs.F_OK, (error) => {
                if (error) {
                    if (error.code === 'ENOENT') {
                        res.setStatus(responseStatuses.NOT_FOUND);
                        res.end();
                    }
                }
            })

            const commandArgs = ['-f', './cgi/mod_php.php', filePath, req.args, 'GET'];

            // if (phpProcesses < 10) {
            //     phpProcesses++;

            let childProcess = spawn('php', commandArgs, { timeout: 2000 }); // TODO timeout not working
            let sent = false;

            childProcess.stdout.on('data', data => {
                if (!sent) {
                    res.setStatus(responseStatuses.OK);
                    res.setHeader('Content-type', mimeTypes['.html']);
                    res.sendHeaders();
                    sent = true;
                }
            });

            childProcess.stderr.on('data', data => {
                res.setStatus(responseStatuses.SERVER_ERROR);
                res.end();
            });

            childProcess.on('error', (error) => {
                res.setStatus(responseStatuses.SERVER_ERROR);
                res.end();
            });

            childProcess.on('close', code => {
                if (code !== 0) {
                    console.log(`child process exited with code ${code}`);
                }
                // phpProcesses --;
            });

            childProcess.stdout.pipe(res.socket);

            // }
            // else {
            //
            // }

        } else {
            res.setHeader('Content-Type', mimeTypes[extname] || 'application/octet-stream');
            fs.createReadStream(filePath, {highWaterMark: CHUNK_SIZE})
                .on('error', function (error) {
                    if (error.code === 'ENOENT') {
                        res.setStatus(responseStatuses.NOT_FOUND);
                        res.end();
                    } else {
                        res.setStatus(responseStatuses.SERVER_ERROR);
                        res.end();
                    }
                })
                .on('ready', function (chunk) {
                    res.setStatus(responseStatuses.OK);
                    res.sendHeaders();
                })
                .pipe(res.socket);
        }
    }

    if (req.method === 'POST') {
        if (extname !== '.php') {
            res.setStatus(responseStatuses.NOT_IMPLEMENTED);
            res.end();
        }

        fs.access(`./cgi/${filePath}`, fs.F_OK, (error) => {
            if (error) {
                if (error.code === 'ENOENT') {
                    res.setStatus(responseStatuses.NOT_FOUND);
                    res.end();
                }
            }
        })

        let reqBuffer = new Buffer('');
        let buf;
        while (true) {
            buf = req.socket.read();
            if (buf === null) break;

            reqBuffer = Buffer.concat([reqBuffer, buf]);
        }
        let reqBody = JSON.parse(reqBuffer.toString());

        const commandArgs = ['-f', './cgi/mod_php.php', filePath, JSON.stringify(reqBody), 'POST'];
        let childProcess = spawn('php', commandArgs);

        childProcess.stdout.on('data', data => {
            res.setStatus(responseStatuses.OK);
            res.setHeader('Content-type', mimeTypes['.html']);
            res.end(data);
        });

        childProcess.stderr.on('data', data => {
            res.setStatus(responseStatuses.SERVER_ERROR);
            res.end();
        });

        childProcess.on('error', (error) => {
            res.setStatus(responseStatuses.SERVER_ERROR);
            res.end();
        });

        childProcess.on('close', code => {
            if (code !== 0) {
                console.log(`child process exited with code ${code}`);
            }
        });
    }
});

webServer.listen(3000);