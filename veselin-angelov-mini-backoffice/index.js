const Koa = require('koa');
const koaPg = require('koa-pg');
const render = require('koa-ejs');
const path = require('path');
require('dotenv').config();

const auth = require('./authentication.js')
const backoffice = require('./backoffice.js')

const app = new Koa();

// app.use(koaPg('postgres://postgres:password@localhost:5432/minibackoffice'));

render(app, {
    root: path.join(__dirname, 'view'),
    layout: 'template',
    viewExt: 'html',
    cache: false,
    debug: false
});


app.use(async (ctx, next) => {
    try {
        await next();
    }
    catch(err) {
        ctx.status = err.status || 500;
        ctx.body = {
            error: err.originalError ? err.originalError.message : err.message
        };
    }
    console.log(`${new Date().toISOString()} ${ctx.ip} ${ctx.method} ${ctx.url} ${ctx.status}`);
});

app.use(auth.routes());
app.use(backoffice.routes());
app.use(auth.allowedMethods());
app.use(backoffice.allowedMethods());

app.listen(3000);