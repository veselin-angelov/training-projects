CREATE TABLE users (
   id SERIAL PRIMARY KEY,
   username TEXT
);

CREATE TABLE payment_methods (
     id SERIAL PRIMARY KEY,
     name TEXT
);

CREATE TABLE subscriptions (
   id SERIAL PRIMARY KEY,
   name TEXT NOT NULL,
   type TEXT NOT NULL,
   amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    status TEXT NOT NULL,
    subscription_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);