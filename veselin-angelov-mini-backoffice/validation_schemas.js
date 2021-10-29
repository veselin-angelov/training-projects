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

const reportRequestValidationSchema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "report1",
    "type": "object",
    "title": "The root schema",
    "required": [
        "filters",
        "excludes",
        "aggregates"
    ],
    "properties": {
        "filters": {
            "$id": "#/properties/filters",
            "type": "object",
            "title": "The filters schema",
            "required": [
                "dateRange",
                "subscriptionName",
                "user",
                "paymentMethod",
                "paymentStatus",
                "paymentAmountRange"
            ],
            "properties": {
                "dateRange": {
                    "$id": "#/properties/filters/properties/dateRange",
                    "type": "object",
                    "title": "The dateRange schema",
                    "required": [
                        "from",
                        "to"
                    ],
                    "properties": {
                        "from": {
                            "$id": "#/properties/filters/properties/dateRange/properties/from",
                            "type": "object",
                            "title": "The from schema",
                            "required": [
                                "value"
                            ],
                            "properties": {
                                "value": {
                                    "$id": "#/properties/filters/properties/dateRange/properties/from/properties/value",
                                    "type": "string",
                                    "title": "The value schema"
                                }
                            },
                            "additionalProperties": false
                        },
                        "to": {
                            "$id": "#/properties/filters/properties/dateRange/properties/to",
                            "type": "object",
                            "title": "The to schema",
                            "required": [
                                "value"
                            ],
                            "properties": {
                                "value": {
                                    "$id": "#/properties/filters/properties/dateRange/properties/to/properties/value",
                                    "type": "string",
                                    "title": "The value schema"
                                }
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                },
                "subscriptionName": {
                    "$id": "#/properties/filters/properties/subscriptionName",
                    "type": "object",
                    "title": "The subscriptionName schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/filters/properties/subscriptionName/properties/value",
                            "type": "string",
                            "title": "The value schema",
                            "minLength": 1
                        }
                    },
                    "additionalProperties": false
                },
                "user": {
                    "$id": "#/properties/filters/properties/user",
                    "type": "object",
                    "title": "The user schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/filters/properties/user/properties/value",
                            "type": "string",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "paymentMethod": {
                    "$id": "#/properties/filters/properties/paymentMethod",
                    "type": "object",
                    "title": "The paymentMethod schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/filters/properties/paymentMethod/properties/value",
                            "type": "string",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "paymentStatus": {
                    "$id": "#/properties/filters/properties/paymentStatus",
                    "type": "object",
                    "title": "The paymentStatus schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/filters/properties/paymentStatus/properties/value",
                            "type": "string",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "paymentAmountRange": {
                    "$id": "#/properties/filters/properties/paymentAmountRange",
                    "type": "object",
                    "title": "The paymentAmountRange schema",
                    "required": [
                        "from",
                        "to"
                    ],
                    "properties": {
                        "from": {
                            "$id": "#/properties/filters/properties/paymentAmountRange/properties/from",
                            "type": "object",
                            "title": "The from schema",
                            "required": [
                                "value"
                            ],
                            "properties": {
                                "value": {
                                    "$id": "#/properties/filters/properties/paymentAmountRange/properties/from/properties/value",
                                    "type": "string",
                                    "title": "The value schema"
                                }
                            },
                            "additionalProperties": false
                        },
                        "to": {
                            "$id": "#/properties/filters/properties/paymentAmountRange/properties/to",
                            "type": "object",
                            "title": "The to schema",
                            "required": [
                                "value"
                            ],
                            "properties": {
                                "value": {
                                    "$id": "#/properties/filters/properties/paymentAmountRange/properties/to/properties/value",
                                    "type": "string",
                                    "title": "The value schema"
                                }
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                }
            },
            "additionalProperties": false
        },
        "excludes": {
            "$id": "#/properties/excludes",
            "type": "object",
            "title": "The excludes schema",
            "required": [
                "dateRangeExclude",
                "subscriptionNameExclude",
                "userExclude",
                "paymentMethodExclude",
                "paymentStatusExclude"
            ],
            "properties": {
                "dateRangeExclude": {
                    "$id": "#/properties/excludes/properties/dateRangeExclude",
                    "type": "object",
                    "title": "The dateRangeExclude schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/excludes/properties/dateRangeExclude/properties/value",
                            "type": "boolean",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "subscriptionNameExclude": {
                    "$id": "#/properties/excludes/properties/subscriptionNameExclude",
                    "type": "object",
                    "title": "The subscriptionNameExclude schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/excludes/properties/subscriptionNameExclude/properties/value",
                            "type": "boolean",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "userExclude": {
                    "$id": "#/properties/excludes/properties/userExclude",
                    "type": "object",
                    "title": "The userExclude schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/excludes/properties/userExclude/properties/value",
                            "type": "boolean",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "paymentMethodExclude": {
                    "$id": "#/properties/excludes/properties/paymentMethodExclude",
                    "type": "object",
                    "title": "The paymentMethodExclude schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/excludes/properties/paymentMethodExclude/properties/value",
                            "type": "boolean",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                },
                "paymentStatusExclude": {
                    "$id": "#/properties/excludes/properties/paymentStatusExclude",
                    "type": "object",
                    "title": "The paymentStatusExclude schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/excludes/properties/paymentStatusExclude/properties/value",
                            "type": "boolean",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                }
            },
            "additionalProperties": false
        },
        "aggregates": {
            "$id": "#/properties/aggregates",
            "type": "object",
            "title": "The aggregates schema",
            "required": [
                "dateRangeAggregate"
            ],
            "properties": {
                "dateRangeAggregate": {
                    "$id": "#/properties/aggregates/properties/dateRangeAggregate",
                    "type": "object",
                    "title": "The dateRangeAggregate schema",
                    "required": [
                        "value"
                    ],
                    "properties": {
                        "value": {
                            "$id": "#/properties/aggregates/properties/dateRangeAggregate/properties/value",
                            "type": "string",
                            "title": "The value schema"
                        }
                    },
                    "additionalProperties": false
                }
            },
            "additionalProperties": false
        }
    },
    "additionalProperties": false
}

module.exports = {
    loginSchema,
    loginResponseSchema,
    reportRequestValidationSchema
};