const Router = require('@koa/router');

const backoffice = new Router();
const jwt = require('koa-jwt');

backoffice.use(jwt({ secret: 'secret', key: 'jwtdata' }));  // TODO

backoffice.get('/', ctx => {
    ctx.body = 'hey from here';
});

module.exports = backoffice;
