const { spawn } = require('child_process');

const Router = require('@koa/router');
const koaBody = require('koa-body');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const Ajv = require("ajv");

const { loginSchema, loginResponseSchema } = require('./schemas.js');

const ajv = new Ajv();
const authentication = new Router();
const saltRounds = 10;

authentication.get('/login', async (ctx) => {
    await ctx.render('login');
})

authentication.post('/login', koaBody(), async ctx => {
    const valid = ajv.validate(loginSchema, ctx.request.body);

    if (!valid) {
        ctx.status = 400
        ctx.body = {
            message: "Bad request!",
        };
        return;
    }

    ctx.request.body.username = ctx.request.body.username.trim();
    ctx.request.body.password = ctx.request.body.password.trim();

    const search = {'username': ctx.request.body.username};
    const pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'select', JSON.stringify(search)]);

    let data = "";
    for await (const chunk of pythonProcess.stdout) {
        data += chunk;
    }

    if (!data) {
        ctx.status = 401
        ctx.body = {
            message: "Incorrect credentials!",
        };
        return;
    }

    const credentials = JSON.parse(data);
    const match = await bcrypt.compare(ctx.request.body.password, credentials.password);

    if (match) {
        const token = jwt.sign({
            'id': credentials.id,
            'username': credentials.username
        }, process.env.SECRET_KEY, {expiresIn: '1h'});

        ctx.status = 200
        ctx.body = {
            message: "Success!",
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

authentication.post('/register', koaBody(), async ctx => {
    const valid = ajv.validate(loginSchema, ctx.request.body);

    if (!valid) {
        ctx.status = 400
        ctx.body = {
            message: "Bad request!",
        };
        return;
    }

    ctx.request.body.username = ctx.request.body.username.trim();
    ctx.request.body.password = ctx.request.body.password.trim();

    const hashedPwd = await bcrypt.hash(ctx.request.body.password, saltRounds);
    const credentials = {'username': ctx.request.body.username, 'password': hashedPwd};

    const pythonProcess = spawn('python3',
        ["../veselin-angelov-db-engine/interface.py", 'insert', JSON.stringify(credentials)]);

    let data = "";
    for await (const chunk of pythonProcess.stdout) {
        data += chunk;
    }

    if (data === 'Inserted a row!\n') {
        ctx.status = 201
        ctx.body = {
            message: "Success!",
        };
    }
    else if (data === 'Username exists!\n') {
        ctx.status = 409
        ctx.body = {
            message: "Username is taken!",
        };
    }
    else {
        console.log(data);
        ctx.status = 400
        ctx.body = {
            message: "Something went wrong! Try again!",
        };
    }
});

module.exports = authentication;