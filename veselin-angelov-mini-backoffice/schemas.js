const loginSchema = {
    type: "object",
    properties: {
        username: {type: "string", minLength: 1},
        password: {type: "string", minLength: 1},
    },
    required: ["username", "password"],
    additionalProperties: false
};

const loginResponseSchema = {
    type: "object",
    properties: {
        message: {type: "string", minLength: 1},
        accessKey: {type: "string", minLength: 1}
    },
    required: ["message"],
    additionalProperties: false
}

module.exports = {
    loginSchema,
    loginResponseSchema
};

const reportRequestSchema = {
    "required": [
        "filters",
        "aggregates"
    ],
    "title": "Report request schema",
    "type": "object",
    "properties": {
        "filters": {
            "required": [
                "fromDate",
                "toDate",
                "subscriptionName",
                "user",
                "paymentMethod",
                "paymentStatus",
                "paymentAmountFrom",
                "paymentAmountTo"
            ],
            "title": "The filters schema",
            "type": "object",
            "properties": {
                "fromDate": {
                    "title": "The fromDate schema",
                    "type": "string"
                },
                "toDate": {
                    "title": "The toDate schema",
                    "type": "string"
                },
                "subscriptionName": {
                    "title": "The subscriptionName schema",
                    "type": "string"
                },
                "user": {
                    "title": "The user schema",
                    "type": "string"
                },
                "paymentMethod": {
                    "title": "The paymentMethod schema",
                    "type": "string"
                },
                "paymentStatus": {
                    "title": "The paymentStatus schema",
                    "type": "string"
                },
                "paymentAmountFrom": {
                    "title": "The paymentAmountFrom schema",
                    "type": "string"
                },
                "paymentAmountTo": {
                    "title": "The paymentAmountTo schema",
                    "type": "string"
                }
            },
            "additionalProperties": true
        },
        "aggregates": {
            "required": [
                "aggregateDate",
                "excludeDate",
                "excludeSubscription",
                "excludeUser",
                "excludePaymentMethod",
                "excludePaymentStatus"
            ],
            "title": "The aggregates schema",
            "type": "object",
            "properties": {
                "aggregateDate": {
                    "title": "The aggregateDate schema",
                    "type": "string"
                },
                "excludeDate": {
                    "title": "The excludeDate schema",
                    "type": "boolean"
                },
                "excludeSubscription": {
                    "title": "The excludeSubscription schema",
                    "type": "boolean"
                },
                "excludeUser": {
                    "title": "The excludeUser schema",
                    "type": "boolean"
                },
                "excludePaymentMethod": {
                    "title": "The excludePaymentMethod schema",
                    "type": "boolean"
                },
                "excludePaymentStatus": {
                    "title": "The excludePaymentStatus schema",
                    "type": "boolean"
                }
            },
            "additionalProperties": true
        }
    },
    "additionalProperties": true
}