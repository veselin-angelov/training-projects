const loginSchema = {
    type: "object",
    properties: {
        username: {type: "string", minLength: 1},
        password: {type: "string", minLength: 1},
    },
    required: ["username", "password"],
    additionalProperties: false
};

module.exports = loginSchema;