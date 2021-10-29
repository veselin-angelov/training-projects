const Router = require('@koa/router');

const backoffice = new Router();
const jwt = require('koa-jwt');

const { reportSchemaConst } = require('./reports_schemas');

backoffice.use(async (ctx, next) => {
    try {
        await next();
    }
    catch(err) {
        if (err.status === 401) {
            ctx.redirect('/login');
        }
        else {
            throw err;
        }
    }
})

backoffice.use(jwt({ secret: process.env.SECRET_KEY, key: 'jwtdata', cookie: 'JWT_TOKEN' }));

backoffice.get('/', async ctx => {
    await ctx.render('home', {
        jwtdata: ctx.state.jwtdata
    });
});

backoffice.get('/reports/payments', async ctx => {
    await ctx.render('report1', {
        schema: reportSchemaConst
    });
});

backoffice.get('/reports/payments-const', async ctx => {
    await ctx.render('report', {
        jwtdata: ctx.state.jwtdata
    });
});

module.exports = backoffice;
