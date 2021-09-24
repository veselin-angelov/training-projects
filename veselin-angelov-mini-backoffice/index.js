const Koa = require('koa');
const render = require('koa-ejs');
const path = require('path');
const { Pool } = require('pg')
const TokenExpiredError = require("jsonwebtoken/lib/TokenExpiredError");

require('dotenv').config();
const auth = require('./authentication.js')
const backoffice = require('./backoffice.js')
const api = require('./api.js')

const app = new Koa();

render(app, {
    root: path.join(__dirname, 'view'),
    layout: 'template',
    viewExt: 'html',
    cache: false,
    debug: false
});


app.use(async (ctx, next) => {
    ctx.pool = new Pool({
        user: 'postgres',
        host: 'localhost',
        database: 'minibackoffice',
        password: 'password',
        port: 5432,
    });
    try {
        await next();
    }
    catch(err) {
        if (err.status === 401) {
            ctx.redirect('/login');
        }
        else {
            ctx.status = err.status || 500;
            ctx.body = {
                error: err.originalError ? err.originalError.message : err.message
            };
        }
    }
    console.log(`${new Date().toISOString()} ${ctx.ip} ${ctx.method} ${ctx.url} ${ctx.status}`);
});

app.use(auth.routes());
app.use(backoffice.routes());
app.use(api.routes());
app.use(auth.allowedMethods());
app.use(backoffice.allowedMethods());
app.use(api.allowedMethods());

app.listen(3000);