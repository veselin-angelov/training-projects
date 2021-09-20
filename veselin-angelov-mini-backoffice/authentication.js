const { spawn } = require('child_process');

const Router = require('@koa/router');
const bcrypt = require('bcrypt');

const authentication = new Router();
const saltRounds = 10;

authentication.use(async (ctx, next) => {
    console.log(`${new Date().toISOString()} ${ctx.ip} ${ctx.method} ${ctx.url}`);
    await next();
    // ctx.pythonProcess.stdout.on('data', (data) => {
    //     console.log(data.toString());
    // });
    ctx.pythonProcess.stderr.on('data', (data) => {
        console.log('Error', data.toString());
    });
})

authentication.get('login', '/login', async ctx => {  // TODO cannot await callback
    // ctx.body = 'Login';
    console.log('l');

    const plaintextPwd = 'lud';
    const search = {'username': 'vesko'};
    ctx.pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'select', JSON.stringify(search)]);

    let credentials;

    ctx.pythonProcess.stdout.on('data', (data) => {
        credentials = JSON.parse(data.toString());
    });

    const match = await bcrypt.compare(plaintextPwd, credentials['password']);

    if (match) {
        console.log('match!');
        ctx.body = {
            status: 200,
            message: "login successfully",
            data: 'eyyy',
        };
    }
    else {
        ctx.body = {
            status: 400,
            message: "Incorrect password! Try again.",
        }
    }
    console.log('asds');
});

authentication.get('register', '/register', async ctx => {
    ctx.body = 'Register';
    console.log('r');

    const plaintextPwd = 'lud';

    const hashedPwd = await bcrypt.hash(plaintextPwd, saltRounds);
    const credentials = {'username': 'vesko', 'password': hashedPwd};

    console.log(credentials);

    ctx.pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'insert', JSON.stringify(credentials)]);

    ctx.pythonProcess.stdout.on('data', (data) => {
        console.log(data.toString());
    });
});

module.exports = authentication;