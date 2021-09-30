const Router = require('@koa/router');

const backoffice = new Router();
const jwt = require('koa-jwt');

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
    ctx.body = `Hello, ${ctx.state.jwtdata.username}`;
    await ctx.render('home', {
        jwtdata: ctx.state.jwtdata
    });
});

backoffice.get('/reports/payments', async ctx => {
    console.log(ctx.state.jwtdata);

    // ctx.pool.query('SELECT * FROM payments;', (err, res) => {
    //     if (err) {
    //         throw err
    //     }
    //     console.log('data:', res.rows)
    // })
    await ctx.render('report', {
        jwtdata: ctx.state.jwtdata
    });
});

module.exports = backoffice;
