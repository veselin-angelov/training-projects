const Koa = require('koa');
const render = require('koa-ejs');
const path = require('path');

const auth = require('./authentication.js')
const backoffice = require('./backoffice.js')

const app = new Koa();
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
        console.log(`${new Date().toISOString()} ${ctx.ip} ${ctx.method} ${ctx.url} ${ctx.status}`);
    } catch(err) {
        console.log(err.status);
        ctx.status = err.status || 500;
        ctx.body = err.message;
    }
});

app.use(auth.routes());
app.use(backoffice.routes());
app.use(auth.allowedMethods());
app.use(backoffice.allowedMethods());

app.listen(3000);