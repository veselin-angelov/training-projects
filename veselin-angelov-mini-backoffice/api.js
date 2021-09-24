const Router = require('@koa/router');

const api = new Router();
const jwt = require('koa-jwt');

api.use(jwt({ secret: process.env.SECRET_KEY, key: 'jwtdata', cookie: 'JWT_TOKEN' }));

api.get('/api/payments', async ctx=> {
    const q = `SELECT p.id, p.date, p.amount, p.status, s.name AS subscription_name, pm.name AS payment_method, u.username AS username
               FROM payments p 
               JOIN subscriptions s on p.subscription_id = s.id     
               JOIN payment_methods pm on pm.id = p.payment_method_id 
               JOIN users u on p.user_id = u.id
               LIMIT 50;`

    await ctx.pool
        .query(q)
        .then(res => {
            ctx.body = res.rows;
            console.log(res.rows[0]);
        })
        .catch(err =>
            setImmediate(() => {
                throw err;
            })
        )
});

module.exports = api;
