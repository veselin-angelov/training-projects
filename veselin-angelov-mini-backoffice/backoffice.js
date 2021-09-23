const Router = require('@koa/router');

const backoffice = new Router();
const jwt = require('koa-jwt');

backoffice.use(jwt({ secret: process.env.SECRET_KEY, key: 'jwtdata', cookie: 'JWT_TOKEN' }));

backoffice.get('/', ctx => {
    console.log(ctx.state.jwtdata);
    // const result = this.pg.db.client.query_('SELECT now()');
    // console.log('result:', result)
    ctx.body = `Hello, ${ctx.state.jwtdata.username}`;
});

module.exports = backoffice;
