const { spawn } = require('child_process');

const Router = require('@koa/router');
const koaBody = require('koa-body');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const Ajv = require("ajv");

const loginSchema = require('./schemas.js');

const ajv = new Ajv();
const authentication = new Router();
const saltRounds = 10;

authentication.get('/login', async (ctx) => {
    await ctx.render('login');
})

authentication.post('/login', koaBody(), async ctx => {
    const valid = ajv.validate(loginSchema, ctx.request.body);

    ctx.request.body.username = ctx.request.body.username.trim();
    ctx.request.body.password = ctx.request.body.password.trim();

    console.log(ctx.request.body);

    if (!valid) {  // TODO validate json schema
        ctx.status = 400
        ctx.body = {
            message: "Bad request!",
        };
        return;
    }

    const search = {'username': ctx.request.body.username};
    ctx.pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'select', JSON.stringify(search)]);

    let data = "";
    for await (const chunk of ctx.pythonProcess.stdout) {
        data += chunk;
    }

    if (!data) {
        ctx.status = 401
        ctx.body = {
            message: "Incorrect credentials!",
        }
        return;
    }

    const credentials = JSON.parse(data);

    const match = await bcrypt.compare(ctx.request.body.password, credentials.password);

    if (match) {
        const token = jwt.sign({'id': credentials.id}, 'secret');
        ctx.status = 200
        ctx.body = {
            message: "Login successfully!",
            accessToken: token,
        };
    }
    else {
        ctx.status = 401
        ctx.body = {
            message: "Incorrect credentials!",
        };
    }
});

authentication.get('/register', async (ctx) => {
    await ctx.render('register');
})

authentication.get('/register', async ctx => { // TODO
    ctx.body = 'Register';
    console.log('r');

    const plaintextPwd = 'lud';

    const hashedPwd = await bcrypt.hash(plaintextPwd, saltRounds);
    const credentials = {'username': 'tzetzo', 'password': hashedPwd};

    console.log(credentials);

    ctx.pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'insert', JSON.stringify(credentials)]);

    ctx.pythonProcess.stdout.on('data', (data) => {
        console.log(data.toString());
    });
});

module.exports = authentication;