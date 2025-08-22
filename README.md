# JWT Generator API

A simple FastAPI-based REST API for generating JSON Web Tokens (JWT). Perfect for testing, development, and prototyping applications that need JWT functionality.

## Features

- 🔐 Generate JWTs with custom payloads
- ⚙️ Configurable JWT options (algorithm, expiration)
- 📝 Automatic payload enrichment (iat, exp timestamps)
- 🚀 Fast and lightweight FastAPI implementation
- 📖 Auto-generated API documentation
- ✅ Easy testing with Hurl

## Installation

### Prerequisites
- Python 3.7+
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

### Setup

#### Option 1: Using uv (Recommended - Fast!)

1. Install uv if you haven't already:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or via pip
   pip install uv
   ```

2. Clone or download the project files

3. Install dependencies and run:
   ```bash
   # Install dependencies
   uv pip install -r requirements.txt
   
   # Or create a virtual environment and install
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   
   # Run the API
   python main.py
   ```

#### Option 2: Using pip (Traditional)

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can view the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoint

### `POST /generate_jwt`

Generates a JWT token with the provided key and payload.

#### Request Body

```json
{
  "key": "your_secret_key",
  "body": {
    "user_id": 123,
    "username": "john_doe",
    "role": "admin"
  },
  "options": {
    "algorithm": "HS256",
    "add_exp": true
  }
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | ✅ Yes | Secret key used to sign the JWT |
| `body` | object | ❌ No | JWT payload/claims (default: `{}`) |
| `options` | object | ❌ No | JWT generation options |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `algorithm` | string | `"HS256"` | JWT signing algorithm |
| `add_exp` | boolean | `true` | Auto-add expiration time (1 hour) |

#### Response

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiam9obl9kb2UiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2OTQ1MjEyMDAsImV4cCI6MTY5NDUyNDgwMH0.signature"
}
```

## Usage Examples

### Basic JWT Generation

```bash
curl -X POST "http://localhost:8000/generate_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my_secret_key",
    "body": {
      "user_id": 123,
      "username": "testuser"
    }
  }'
```

### Custom Algorithm and No Expiration

```bash
curl -X POST "http://localhost:8000/generate_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my_secret_key",
    "body": {
      "service": "api",
      "permissions": ["read", "write"]
    },
    "options": {
      "algorithm": "HS512",
      "add_exp": false
    }
  }'
```

## Testing with Hurl

A Hurl test file is included for easy API testing:

```bash
# Run the simple JWT generation test
hurl --test simple_jwt_capture.hurl
```

The test will:
1. Generate a JWT token
2. Capture it in a variable for potential reuse
3. Validate the response format

## Automatic Payload Enhancement

The API automatically adds these fields to your JWT payload if not present:

- `iat` (issued at): Current UTC timestamp
- `exp` (expiration): Current UTC timestamp + 1 hour (if `add_exp: true`)

## Supported JWT Algorithms

- HS256 (HMAC SHA-256) - Default
- HS384 (HMAC SHA-384)
- HS512 (HMAC SHA-512)
- RS256 (RSA SHA-256)
- RS384 (RSA SHA-384)
- RS512 (RSA SHA-512)
- ES256 (ECDSA SHA-256)
- ES384 (ECDSA SHA-384)
- ES512 (ECDSA SHA-512)

*Note: RSA and ECDSA algorithms require appropriate key formats*

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request format or missing required fields
- `500 Internal Server Error`: Server-side errors (invalid algorithms, etc.)

Example error response:
```json
{
  "detail": "Internal server error: Invalid algorithm specified"
}
```

## Development

### Project Structure

```
jwt-generator-api/
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── simple_jwt_capture.hurl    # Hurl test file
└── README.md                  # This file
```

### Dependencies

- **FastAPI**: Modern web framework for APIs
- **uvicorn**: ASGI server for running FastAPI
- **PyJWT**: JWT implementation for Python

## Security Considerations

⚠️ **Important Security Notes:**

1. **Secret Key Management**: Never hardcode secret keys in production. Use environment variables or secure key management systems.

2. **Key Strength**: Use strong, randomly generated secret keys (minimum 256 bits for HS256).

3. **Algorithm Selection**: Be explicit about allowed algorithms to prevent algorithm confusion attacks.

4. **Production Use**: This API is designed for development/testing. For production, consider additional security measures like rate limiting, input validation, and secure key storage.

## License

This project is provided as-is for educational and development purposes.