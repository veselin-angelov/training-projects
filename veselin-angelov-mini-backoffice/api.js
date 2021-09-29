const Router = require('@koa/router');

const api = new Router();
const jwt = require('koa-jwt');
const koaBody = require("koa-body");

Date.prototype.addHours = function(h){
    this.setHours(this.getHours()+h);
    return this;
}

Date.prototype.addDays = function (days) {
    this.setDate(this.getDate() + days);
    return this;
};

function checkJSONElementsNotNull (object) {
    for (const key in object) {
        if (object[key]) {
            return true;
        }
    }
}

api.use(jwt({ secret: process.env.SECRET_KEY, key: 'jwtdata', cookie: 'JWT_TOKEN' }));

api.get('/api/statuses', async ctx=> {
    ctx.body = ['COMPLETE', 'PENDING', 'FAILED'];
});

api.get('/api/payment-methods', async ctx=> {
    ctx.body = ['VISA', 'MasterCard', 'PayPal'];
});

api.get('/api/date-aggregates', async ctx=> {
    ctx.body = ['Daily', 'Weekly', 'Monthly', 'Yearly'];
});

api.post('/api/payments', koaBody(), async ctx=> {

    console.log(ctx.request.body);

    ctx.body = ctx.request.body;

    let createQuery = (select) =>
        `SELECT ${select}
            FROM payments p
            JOIN subscriptions s on p.subscription_id = s.id
            JOIN payment_methods pm on pm.id = p.payment_method_id
            JOIN users u on p.user_id = u.id`;

    let sum_q = `SELECT SUM(p.amount) AS total, COUNT(*) AS count
            FROM payments p
            JOIN subscriptions s on p.subscription_id = s.id
            JOIN payment_methods pm on pm.id = p.payment_method_id
            JOIN users u on p.user_id = u.id`;

    let q;
    let groupParameters = [];
    let orderParameters = [];

    if (checkJSONElementsNotNull(ctx.body.aggregates)) {
        let aggregateParameters = [];

        if (ctx.body.aggregates.aggregateDate) {
            groupParameters.push(aggregateParameters.length + 1);
            orderParameters.push(aggregateParameters.length + 1);

            if (ctx.body.aggregates.aggregateDate === 'Daily') {
                aggregateParameters.push(`to_char(date_trunc('day', p.date), 'YYYY-MM-DD') AS date`);
            }
            else if (ctx.body.aggregates.aggregateDate === 'Weekly') {
                aggregateParameters.push(`to_char(date_trunc('week', p.date), 'WW / YYYY') AS date`);
            }
            else if (ctx.body.aggregates.aggregateDate === 'Monthly') {
                aggregateParameters.push(`to_char(date_trunc('month', p.date), 'Month YYYY') AS date`);
            }
            else if (ctx.body.aggregates.aggregateDate === 'Yearly') {
                aggregateParameters.push(`to_char(date_trunc('year', p.date), 'YYYY') AS date`);
            }
        }

        if (ctx.body.aggregates.aggregateSubscription) {
            groupParameters.push(aggregateParameters.length + 1);
            orderParameters.push(aggregateParameters.length + 1);
            aggregateParameters.push(`s.name AS subscription_name`);
        }

        if (ctx.body.aggregates.aggregateUser) {
            groupParameters.push(aggregateParameters.length + 1);
            orderParameters.push(aggregateParameters.length + 1);
            aggregateParameters.push(`u.username AS username`);
        }

        if (ctx.body.aggregates.aggregatePaymentMethod) {
            groupParameters.push(aggregateParameters.length + 1);
            orderParameters.push(aggregateParameters.length + 1);
            aggregateParameters.push(`pm.name AS payment_method`);
        }

        if (ctx.body.aggregates.aggregatePaymentStatus) {
            groupParameters.push(aggregateParameters.length + 1);
            orderParameters.push(aggregateParameters.length + 1);
            aggregateParameters.push(`p.status AS status`);
        }

        let selectParameters = [...aggregateParameters];
        selectParameters.push('SUM(p.amount) AS amount');
        q = createQuery(selectParameters.join(', '));
    }
    else {
        q = createQuery('p.id, p.date, p.amount, p.status, s.name AS subscription_name, pm.name AS payment_method, u.username AS username');
    }

    if (checkJSONElementsNotNull(ctx.body.filters)) {
        let q_filters = [];

        if (ctx.body.filters.fromDate) {
                q_filters.push(`p.date >= '${ctx.body.filters.fromDate}'`);
        }
        if (ctx.body.filters.toDate) {
            q_filters.push(`p.date < '${new Date(ctx.body.filters.toDate).addDays(1).toISOString().substring(0, 10)}'`);
        }
        if (ctx.body.filters.paymentAmountFrom) {
            q_filters.push(`p.amount >= ${ctx.body.filters.paymentAmountFrom}`);
        }
        if (ctx.body.filters.paymentAmountTo) {
            q_filters.push(`p.amount <= ${ctx.body.filters.paymentAmountTo}`);
        }
        if (ctx.body.filters.paymentStatus && ctx.body.filters.paymentStatus !== 'All') {
            q_filters.push(`p.status = '${ctx.body.filters.paymentStatus}'`);
        }
        if (ctx.body.filters.paymentMethod && ctx.body.filters.paymentMethod !== 'All') {
            q_filters.push(`pm.name = '${ctx.body.filters.paymentMethod}'`);
        }
        if (ctx.body.filters.subscriptionName) {
            q_filters.push(`s.name LIKE '%${ctx.body.filters.subscriptionName}%'`);
        }
        if (ctx.body.filters.user) {
            q_filters.push(`u.username LIKE '%${ctx.body.filters.user}%'`);
        }

        let conditions = '';
        conditions += ' WHERE ';
        conditions += q_filters.join(' AND ');

        sum_q += conditions;
        q += conditions;
    }

    if (groupParameters.length > 0) {
        q += ' GROUP BY ' + groupParameters.join(', ') + ' ORDER BY ' + orderParameters.join(', ');
    }

    else {
        q += ' ORDER BY p.date';
    }

    console.log(q);
    console.log(sum_q);

    let data = {};

    await ctx.pool
        .query(sum_q)
        .then(res => {
            data.rowsCount = res.rows[0].count;
            data.totalAmount = res.rows[0].total;
        })
        .catch(err =>
            setImmediate(() => {
                throw err;
            })
        )

    await ctx.pool
        .query(q)
        .then(res => {
            data.rowsData = res.rows;
        })
        .catch(err =>
            setImmediate(() => {
                throw err;
            })
        )

    ctx.body = data;
});

module.exports = api;
