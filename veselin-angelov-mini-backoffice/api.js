const Router = require('@koa/router');
const jwt = require('koa-jwt');
const koaBody = require("koa-body");
const lodashClonedeep = require('lodash.clonedeep');
const Ajv = require("ajv");

const { reportRequestValidationSchema } = require("./validation_schemas");
const { reportSchemaConst } = require('./reports_schemas');

const ajv = new Ajv();
const api = new Router();

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
    const valid = ajv.validate(reportRequestValidationSchema, ctx.request.body);

    if (!valid) {
        ctx.status = 400
        ctx.body = ajv.errors;
        console.log(ajv.errors);
        return;
    }

    ctx.body = ctx.request.body;

    let reportSchema = lodashClonedeep(reportSchemaConst);

    let filters = [];

    /**
     * Handling the filters category in the schema
     */
    for (const element in reportSchema.filters) {
        if (!reportSchema.filters[element].hasOwnProperty('value')) {
            if (element.includes('Range')) {
                reportSchema.filters[element].from.value = ctx.body.filters[element].from.value;
                reportSchema.filters[element].to.value = ctx.body.filters[element].to.value;

                reportSchema.filters[element].from.dbExpression = reportSchema.filters[element].from.dbExpression.replace(`$${element}From_value`, reportSchema.filters[element].from.value);
                reportSchema.filters[element].to.dbExpression = reportSchema.filters[element].to.dbExpression.replace(`$${element}To_value`, reportSchema.filters[element].to.value);

                if (reportSchema.filters[element].from.value !== '') {
                    filters.push(reportSchema.filters[element].from.dbExpression);
                }
                if (reportSchema.filters[element].to.value !== '') {
                    filters.push(reportSchema.filters[element].to.dbExpression);
                }
            }
            else {
                throw Error;
            }
        }
        else {
            reportSchema.filters[element].value = ctx.body.filters[element].value;
            reportSchema.filters[element].dbExpression = reportSchema.filters[element].dbExpression.replace(`$${element}_value`, reportSchema.filters[element].value);
            if (reportSchema.filters[element].value !== '') {
                filters.push(reportSchema.filters[element].dbExpression);
            }
        }
    }

    /**
     * Handling the excludes category in the schema
     */
    for (const element in reportSchema.excludes) {
        reportSchema.excludes[element].value = ctx.body.excludes[element].value;

        if (reportSchema.excludes[element].value) {
            reportSchema.countExcludesAndAggregates += 1;
            const elementIndex = reportSchema.filters[`${element.replace('Exclude', '')}`].selectArrayIndex;
            reportSchema.excludesFromArray.push(elementIndex);
        }
    }

    /**
     * Handling the aggregates category in the schema
     */
    for (const element in reportSchema.aggregates) {
        reportSchema.aggregates[element].value = ctx.body.aggregates[element].value;

        if (reportSchema.aggregates[element].value) {
            reportSchema.countExcludesAndAggregates += 1;

            if (reportSchema.aggregates[element].type === 'date') {
                const elementColumnName = reportSchema.filters[`${element.replace('Aggregate', '')}`].dbColumnName;
                const elementIndex = reportSchema.filters[`${element.replace('Aggregate', '')}`].selectArrayIndex - 1;

                if (reportSchema.aggregates[element].value === 'Daily') {
                    reportSchema.selects[elementIndex].value = (`to_char(date_trunc('day', ${elementColumnName}), 'YYYY-MM-DD') AS date`);
                } else if (reportSchema.aggregates[element].value === 'Weekly') {
                    reportSchema.selects[elementIndex].value = (`to_char(date_trunc('week', ${elementColumnName}), 'WW / YYYY') AS date`);
                } else if (reportSchema.aggregates[element].value === 'Monthly') {
                    reportSchema.selects[elementIndex].value = (`to_char(date_trunc('month', ${elementColumnName}), 'Month YYYY') AS date`);
                } else if (reportSchema.aggregates[element].value === 'Yearly') {
                    reportSchema.selects[elementIndex].value = (`to_char(date_trunc('year', ${elementColumnName}), 'YYYY') AS date`);
                } else {
                    throw Error;
                }
                continue;
            }
            throw Error;
        }
    }


    if (reportSchema.countExcludesAndAggregates > 0) {
        for (const element of reportSchema.excludesFromArray) {
            reportSchema.groupBy.splice(reportSchema.groupBy.indexOf(element), 1);
            const index = element - 1;
            const dbColumnName = reportSchema.selects[index].value.substr(0, reportSchema.selects[index].value.indexOf('AS'));
            reportSchema.selects[index].value = reportSchema.selects[index].value.replace(dbColumnName, `'(' || COUNT(DISTINCT ${dbColumnName}) || ')' `);
        }
    }

    let conditions = '';
    if (filters.length > 0) {
        conditions += 'WHERE ' + filters.join(' AND ');
    }

    let groupStatements = '';
    let orderStatements = '';
    if (reportSchema.groupBy.length > 0) {
        groupStatements += 'GROUP BY ' + reportSchema.groupBy.join(', ');
        orderStatements += 'ORDER BY ' + reportSchema.groupBy.join(', ');
    }

    let selects = [];
    for (const select of reportSchema.selects) {
        selects.push(select.value);
    }

    const q = reportSchema.query(selects.join(', '), conditions, groupStatements, orderStatements);

    let data = {};

    if (reportSchema.hasOwnProperty('sumQuery') && reportSchema.sumQuery !== '') {
        const sum_q = reportSchema.sumQuery(conditions);

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
    }

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
