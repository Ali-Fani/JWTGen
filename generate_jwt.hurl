POST http://localhost:8080/generate_jwt
Content-Type: application/json

{
  "key": "my_secret_key",
  "body": {
    "user_id": 123,
    "username": "testuser"
  }
}

HTTP 200
[Captures]
jwt_token: jsonpath "$.token"