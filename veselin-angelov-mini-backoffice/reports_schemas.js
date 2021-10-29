
const reportSchemaConst = {
    query: (select, filter, group, order) => `
            SELECT ${select}
            FROM payments p
            JOIN subscriptions s on p.subscription_id = s.id
            JOIN payment_methods pm on pm.id = p.payment_method_id
            JOIN users u on p.user_id = u.id
            ${filter}
            ${group}
            ${order}
        `,
    sumQuery: (filter) => `
            SELECT SUM(p.amount) AS total
            FROM payments p
            JOIN subscriptions s on p.subscription_id = s.id
            JOIN payment_methods pm on pm.id = p.payment_method_id
            JOIN users u on p.user_id = u.id
            ${filter}
        `,
    endpoint: '/api/payments',
    selects: [
        {
            label: 'ID',
            value: 'p.id AS id',
            type: 'number'
        },
        {
            label: 'Date',
            value: 'p.date AS date',
            type: 'date'
        },
        {
            label: 'Subscription name',
            value: 's.name AS subscription_name',
            type: 'text'
        },
        {
            label: 'Username',
            value: 'u.username AS username',
            type: 'text'
        },
        {
            label: 'Payment method',
            value: 'pm.name AS payment_method',
            type: 'enum'
        },
        {
            label: 'Payment status',
            value: 'p.status AS status',
            type: 'enum'
        },
        {
            label: 'Amount',
            value: 'SUM(p.amount) AS amount',
            type: 'money'
        }
    ],
    groupBy: [1, 2, 3, 4, 5, 6], // TODO da go dobavq gore v selects
    excludesFromArray: [1], // rm rf
    countExcludesAndAggregates: 0, // rm rf
    filters: {
        dateRange: {
            label: 'Date',
            type: 'date',
            htmlType: 'text',
            selectArrayIndex: 2,
            dbColumnName: 'p.date',
            from: {
                dbExpression: `p.date >= '$dateRangeFrom_value'`,
                value: ''
            },
            to: {
                dbExpression: `p.date < '$dateRangeTo_value'`,
                value: ''
            }
        },
        subscriptionName: {
            label: 'Subscription name',
            type: 'text',
            htmlType: 'text',
            selectArrayIndex: 3,
            dbColumnName: 's.name',
            dbExpression: `s.name LIKE '%$subscriptionName_value%'`,
            value: ''
        },
        user: {
            label: 'Username',
            type: 'text',
            htmlType: 'text',
            selectArrayIndex: 4,
            dbColumnName: 'u.username',
            dbExpression: `u.username LIKE '%$user_value%'`,
            value: ''
        },
        paymentMethod: {
            label: 'Payment method',
            type: 'enum',
            htmlType: 'text',
            selectArrayIndex: 5,
            dbColumnName: 'pm.name',
            dbExpression: 'pm.name = $paymentMethod_value',
            predefinedValues: ['VISA', 'MasterCard', 'PayPal'],
            value: ''
        },
        paymentStatus: {
            label: 'Payment status',
            type: 'enum',
            htmlType: 'text',
            selectArrayIndex: 6,
            dbColumnName: 'p.status',
            dbExpression: 'p.status = $paymentStatus_value',
            predefinedValues: ['COMPLETE', 'PENDING', 'FAILED'],
            value: ''
        },
        paymentAmountRange: {
            label: 'Payment amount',
            type: 'money',
            htmlType: 'number',
            selectArrayIndex: 7,
            dbColumnName: 'p.amount',
            from: {
                dbExpression: 'p.amount >= $paymentAmountRangeFrom_value',
                value: ''
            },
            to: {
                dbExpression: 'p.amount <= $paymentAmountRangeTo_value',
                value: ''
            }
        }
    },
    excludes: {
        dateRangeExclude: {
            type: 'boolean',
            value: false,
        },
        subscriptionNameExclude: {
            type: 'boolean',
            value: false
        },
        userExclude: {
            type: 'boolean',
            value: false
        },
        paymentMethodExclude: {
            type: 'boolean',
            value: false
        },
        paymentStatusExclude: {
            type: 'boolean',
            value: false
        },
    },
    aggregates: {
        dateRangeAggregate: {
            type: 'date',
            htmlType: 'text',
            predefinedValues: ['Daily', 'Weekly', 'Monthly', 'Yearly'],
            value: ''
        }
    }
};

module.exports = {reportSchemaConst};


// const reportSchemaConst1 = {
//     query: (select, filter, group, order) => `
//             SELECT
//                    $filter_1_groupbyexpr AS id,
//                     ${select},
//                     SUM(amount)
//             FROM payments p
//             JOIN subscriptions s on p.subscription_id = s.id
//             JOIN payment_methods pm on pm.id = p.payment_method_id
//             JOIN users u on p.user_id = u.id
//     WHERE
//         $filter_1_filterexpr -----> TRUE
//
//         ${filter}
//             ${group}
//             ${order}
//     GROUP BY $filter_1_groupby_number;
//         `,
//     sumQuery: (filter) => `
//             SELECT SUM(p.amount) AS total
//             FROM payments p
//             JOIN subscriptions s on p.subscription_id = s.id
//             JOIN payment_methods pm on pm.id = p.payment_method_id
//             JOIN users u on p.user_id = u.id
//             ${filter}
//         `,
//     SumColumns: ['amount'] ,
//     endpoint: '/api/payments',
//     filters2: [
//         {
//             "groupbyexpr": "date_trunc($VAL_FROM_FILTER, p.date)",
//         }
//     ],
//
//     selects: [
//         {
//             label: 'ID',
//             value: 'p.id AS id',
//             value_nwq: 'p.id',
//             // COUNT(p.id)
//             type: 'number'
//         },
//         {
//             label: 'Date',
//             value: 'p.date AS date',
//             type: 'date'
//         },
//         {
//             label: 'Subscription name',
//             value: 's.name AS subscription_name',
//             type: 'text'
//         },
//         {
//             label: 'Username',
//             value: 'u.username AS username',
//             type: 'text'
//         },
//         {
//             label: 'Payment method',
//             value: 'pm.name AS payment_method',
//             type: 'enum'
//         },
//         {
//             label: 'Payment status',
//             value: 'p.status AS status',
//             type: 'enum'
//         },
//         {
//             label: 'Amount',
//             value: 'SUM(p.amount) AS amount',
//             type: 'money'
//         }
//     ],
//     groupBy: [1, 2, 3, 4, 5, 6], // TODO da go dobavq gore v selects
//     excludesFromArray: [1], // rm rf
//     countExcludesAndAggregates: 0, // rm rf
//     filters: {
//         dateRange: {
//             label: 'Date',
//             type: 'date',
//             htmlType: 'text',
//             selectArrayIndex: 2,
//             dbColumnName: 'p.date',
//             from: {
//                 dbExpression: `p.date >= '$dateRangeFrom_value'`,
//                 value: ''
//             },
//             to: {
//                 dbExpression: `p.date < '$dateRangeTo_value'`,
//                 value: ''
//             }
//         },
//         subscriptionName: {
//             label: 'Subscription name',
//             type: 'text',
//             htmlType: 'text',
//             selectArrayIndex: 3,
//             dbColumnName: 's.name',
//             dbExpression: `s.name LIKE '%$subscriptionName_value%'`,
//             value: ''
//         },
//         user: {
//             label: 'Username',
//             type: 'text',
//             htmlType: 'text',
//             selectArrayIndex: 4,
//             dbColumnName: 'u.username',
//             dbExpression: `u.username LIKE '%$user_value%'`,
//             value: ''
//         },
//         paymentMethod: {
//             label: 'Payment method',
//             type: 'enum',
//             htmlType: 'text',
//             selectArrayIndex: 5,
//             dbColumnName: 'pm.name',
//             dbExpression: 'pm.name = $paymentMethod_value',
//             predefinedValues: ['VISA', 'MasterCard', 'PayPal'],
//             value: ''
//         },
//         paymentStatus: {
//             label: 'Payment status',
//             type: 'enum',
//             htmlType: 'text',
//             selectArrayIndex: 6,
//             dbColumnName: 'p.status',
//             dbExpression: 'p.status = $paymentStatus_value',
//             predefinedValues: ['COMPLETE', 'PENDING', 'FAILED'],
//             value: ''
//         },
//         paymentAmountRange: {
//             label: 'Payment amount',
//             type: 'money',
//             htmlType: 'number',
//             selectArrayIndex: 7,
//             dbColumnName: 'p.amount',
//             from: {
//                 dbExpression: 'p.amount >= $paymentAmountRangeFrom_value',
//                 value: ''
//             },
//             to: {
//                 dbExpression: 'p.amount <= $paymentAmountRangeTo_value',
//                 value: ''
//             }
//         }
//     },
//     excludes: {
//         dateRangeExclude: {
//             type: 'boolean',
//             value: false,
//         },
//         subscriptionNameExclude: {
//             type: 'boolean',
//             value: false
//         },
//         userExclude: {
//             type: 'boolean',
//             value: false
//         },
//         paymentMethodExclude: {
//             type: 'boolean',
//             value: false
//         },
//         paymentStatusExclude: {
//             type: 'boolean',
//             value: false
//         },
//     },
//     aggregates: {
//         dateRangeAggregate: {
//             type: 'date',
//             htmlType: 'text',
//             predefinedValues: ['Daily', 'Weekly', 'Monthly', 'Yearly'],
//             value: ''
//         }
//     }
// };


// TODO hasOwnProperty remove