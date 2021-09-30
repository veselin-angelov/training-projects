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

api.use(async (ctx, next) => {
    try {
        await next();
    }
    catch(err) {
        if (err.status === 401) {
            ctx.status = 302;
            ctx.body = {
                redirect: '/login'
            };
        }
        else {
            throw err;
        }
    }
});

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
    // let reportSchema = {
    //     filters: {
    //         fromDate: {
    //             type: 'date',
    //             value: ''
    //         },
    //         toDate: {
    //             type: 'date',
    //             value: '',
    //             extraDays: 1
    //         },
    //         subscriptionName: {
    //             type: 'string',
    //             value: ''
    //         },
    //         user: {
    //             type: 'string',
    //             value: ''
    //         },
    //         paymentMethod: {
    //             type: 'string',
    //             value: ''
    //         },
    //         paymentStatus: {
    //             type: 'string',
    //             value: ''
    //         },
    //         paymentAmountFrom: {
    //             type: 'string',
    //             value: ''
    //         },
    //         paymentAmountTo: {
    //             type: 'string',
    //             value: ''
    //         },
    //     },
    //     aggregates: {
    //         excludeDate: {
    //             type: 'boolean',
    //             value: false,
    //             groups: {
    //                 aggregateDate: {
    //                     type: 'string',
    //                     value: ''
    //                 }
    //             }
    //         },
    //         excludeSubscription: {
    //             type: 'boolean',
    //             value: false
    //         },
    //         excludeUser: {
    //             type: 'boolean',
    //             value: false
    //         },
    //         excludePaymentMethod: {
    //             type: 'boolean',
    //             value: false
    //         },
    //         excludePaymentStatus: {
    //             type: 'boolean',
    //             value: false
    //         },
    //     }
    // }
    //
    //
    // console.log(ctx.body);

    // for (const element in ctx.body) {
    //     for (const key in ctx.body[element]) {
    //         console.log(key);
    //         console.log(reportSchema[element][key]);
    //         console.log(ctx.body[element][key]);
    //         reportSchema[element][key].value = ctx.body[element][key];
    //     }
    // }
    //
    // console.log(reportSchema);
    ctx.body = ctx.request.body;


    let createQuery = (select, filter, group, order) => `
        SELECT SUM(p.amount) AS amount, ${select}
        FROM payments p
        JOIN subscriptions s on p.subscription_id = s.id
        JOIN payment_methods pm on pm.id = p.payment_method_id
        JOIN users u on p.user_id = u.id
        ${filter}
        GROUP BY ${group}
        ORDER BY ${order};
    `;

    let createSumQuery = (filter) => `
        SELECT SUM(p.amount) AS total
        FROM payments p
        JOIN subscriptions s on p.subscription_id = s.id
        JOIN payment_methods pm on pm.id = p.payment_method_id
        JOIN users u on p.user_id = u.id
        ${filter}
    `;

    let select = ['p.id', 'p.date', 'p.status', 's.name AS subscription_name', 'pm.name AS payment_method', 'u.username AS username'];
    let group = [2, 3, 4, 5, 6, 7];
    let filters = [];

    if (checkJSONElementsNotNull(ctx.body.filters)) {
        if (ctx.body.filters.fromDate) {
            filters.push(`p.date >= '${new Date(ctx.body.filters.fromDate).toISOString()}'`);
        }
        if (ctx.body.filters.toDate) {
            filters.push(`p.date < '${new Date(ctx.body.filters.toDate).addDays(1).toISOString()}'`);
        }
        if (ctx.body.filters.paymentAmountFrom) {
            filters.push(`p.amount >= ${ctx.body.filters.paymentAmountFrom}`);
        }
        if (ctx.body.filters.paymentAmountTo) {
            filters.push(`p.amount <= ${ctx.body.filters.paymentAmountTo}`);
        }
        if (ctx.body.filters.paymentStatus && ctx.body.filters.paymentStatus !== 'All') {
            filters.push(`p.status = '${ctx.body.filters.paymentStatus}'`);
        }
        if (ctx.body.filters.paymentMethod && ctx.body.filters.paymentMethod !== 'All') {
            filters.push(`pm.name = '${ctx.body.filters.paymentMethod}'`);
        }
        if (ctx.body.filters.subscriptionName) {
            filters.push(`s.name LIKE '%${ctx.body.filters.subscriptionName}%'`);
        }
        if (ctx.body.filters.user) {
            filters.push(`u.username LIKE '%${ctx.body.filters.user}%'`);
        }
    }

    if (checkJSONElementsNotNull(ctx.body.aggregates)) {
        // select.splice(0, 1);
        // select[0] = "'All' AS id";
        select[0] = "'(' || COUNT(DISTINCT p.id) || ')' AS id";
        group.splice(0, 1);

        if (ctx.body.aggregates.excludeDate) {
            const index = select.indexOf('p.date');
            select[index] = 'COUNT(DISTINCT p.date) AS date';
            const groupIndex = group.indexOf(index + 2);
            group.splice(groupIndex, 1);
        } else {
            if (ctx.body.aggregates.aggregateDate) {
                if (ctx.body.aggregates.aggregateDate === 'Daily') {
                    select[1] = (`to_char(date_trunc('day', p.date), 'YYYY-MM-DD') AS date`);
                } else if (ctx.body.aggregates.aggregateDate === 'Weekly') {
                    select[1] = (`to_char(date_trunc('week', p.date), 'WW / YYYY') AS date`);
                } else if (ctx.body.aggregates.aggregateDate === 'Monthly') {
                    select[1] = (`to_char(date_trunc('month', p.date), 'Month YYYY') AS date`);
                } else if (ctx.body.aggregates.aggregateDate === 'Yearly') {
                    select[1] = (`to_char(date_trunc('year', p.date), 'YYYY') AS date`);
                }
            }
        }

        if (ctx.body.aggregates.excludeSubscription) {
            const index = select.indexOf('s.name AS subscription_name');
            select[index] = 'COUNT(DISTINCT s.name) AS subscription_name';
            const groupIndex = group.indexOf(index + 2);
            group.splice(groupIndex, 1);
        }

        if (ctx.body.aggregates.excludeUser) {
            const index = select.indexOf('u.username AS username');
            select[index] = 'COUNT(DISTINCT u.username) AS username';
            const groupIndex = group.indexOf(index + 2);
            group.splice(groupIndex, 1);
        }

        if (ctx.body.aggregates.excludePaymentMethod) {
            const index = select.indexOf('pm.name AS payment_method');
            select[index] = 'COUNT(DISTINCT pm.name) AS payment_method';
            const groupIndex = group.indexOf(index + 2);
            group.splice(groupIndex, 1);
        }

        if (ctx.body.aggregates.excludePaymentStatus) {
            const index = select.indexOf('p.status');
            select[index] = 'COUNT(DISTINCT p.status) AS status';
            const groupIndex = group.indexOf(index + 2);
            group.splice(groupIndex, 1);
        }
    }

    let conditions = '';
    if (filters.length > 0) {
        conditions += 'WHERE ' + filters.join(' AND ');
    }

    const q = createQuery(select.join(', '), conditions, group.join(', '), group.join(', '));
    const sum_q = createSumQuery(conditions);

    console.log(q);
    console.log(sum_q);

    let data = {};

    await ctx.pool
        .query(sum_q)
        .then(res => {
            data.totalAmount = res.rows[0].total;
        })
        .catch(err =>
            setImmediate(() => {
                throw err;
            })
        );

    await ctx.pool
        .query(q)
        .then(res => {
            data.rowsCount = res.rowCount;
            data.rowsData = res.rows;
        })
        .catch(err =>
            setImmediate(() => {
                throw err;
            })
        );

    ctx.body = data;
});

module.exports = api;
