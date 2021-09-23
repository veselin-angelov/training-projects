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