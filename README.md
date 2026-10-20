# CRUD Service API

A RESTful CRUD API built with **FastAPI**, designed to manage items through authenticated endpoints. The service supports creating, retrieving, updating, and deleting items, with HTTP Bearer authentication protecting item operations.

## Features

- Create new items
- Retrieve all items
- Retrieve a single item by ID
- Update existing items
- Delete items
- HTTP Bearer token authentication
- Request validation using Pydantic
- Automatic interactive API documentation

## Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **ORM:** SQLAlchemy
- **Database:** MySQL (if configured in the database connection)
- **Authentication:** HTTP Bearer tokens
- **Validation:** Pydantic
- **API Specification:** OpenAPI 3.1

## Project Structure

```text
project/
├── data_base/
│   └── database.py
├── crud/
│   ├── model.py
│   └── crud.py
├── auth/
│   ├── model.py
│   └── auth.py
├── requirements.txt
└── .env
```

Adjust the structure above to match your actual project files.

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv pyjwt pwdlib[argon2]
```

Install any additional database driver or authentication dependencies required by your implementation.

### 4. Configure environment variables

Create a `.env` file in the location expected by your application.

Example:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name

JWT_KEY=replace_with_a_secure_secret
JWT_ALGO=HS256
JWT_ACCESS_TOKEN_TIME_MIN=15
JWT_REFRESH_TOKEN_TIME_DAYS=7
```

Use a strong, randomly generated JWT secret. Never commit real credentials or secrets to version control.

### 5. Run the application

```bash
uvicorn main:app --reload
```

Replace `main` with the actual Python module containing your FastAPI instance.

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI schema:** `http://127.0.0.1:8000/openapi.json`

## API Endpoints

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| GET | `/` | Not required | Check service health |
| GET | `/item` | Bearer token | Retrieve all items |
| POST | `/item` | Bearer token | Create an item |
| PUT | `/item` | Bearer token | Update an item |
| GET | `/item/{item_id}` | Bearer token | Retrieve one item |
| DELETE | `/item/{item_id}` | Bearer token | Delete an item |

## Request Examples

### 1. Health Check

```http
GET /
```

Example response:

```json
{
  "status": "CRUD service is running"
}
```

The exact response depends on your implementation.

### 2. Create an Item

```http
POST /item
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request body:

```json
{
  "item_name": "Laptop",
  "item_description": "Development laptop"
}
```

The `item_name` field is required and must contain between 1 and 100 characters. The optional `item_description` defaults to an empty string and supports up to 200 characters.

### 3. Retrieve All Items

```http
GET /item
Authorization: Bearer <access_token>
```

Returns the collection of items according to your endpoint implementation.

### 4. Retrieve an Item

```http
GET /item/1
Authorization: Bearer <access_token>
```

Replace `1` with the desired item ID.

### 5. Update an Item

```http
PUT /item
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request body:

```json
{
  "item_id": 1,
  "item_name": "Updated Laptop",
  "item_description": "Updated development laptop"
}
```

All three fields are required by the current OpenAPI schema.

### 6. Delete an Item

```http
DELETE /item/1
Authorization: Bearer <access_token>
```

Replace `1` with the ID of the item to delete.

## Authentication

Protected endpoints require a valid HTTP Bearer token in the `Authorization` header.

```http
Authorization: Bearer <access_token>
```

Obtain an access token from your authentication service, then include it in requests to this CRUD service.

If your authentication service issues both access and refresh tokens, use the **access token** to access protected CRUD endpoints. Refresh tokens should be used only with the appropriate refresh endpoint.

## Validation and Error Handling

The API uses Pydantic validation to check incoming request bodies and FastAPI to generate validation responses.

Common HTTP status codes include:

| Status | Meaning |
|---|---|
| 200 | Request completed successfully |
| 401 | Missing or invalid authentication credentials |
| 403 | Authenticated user lacks permission, if enforced |
| 404 | Requested item not found, if handled by the endpoint |
| 422 | Request validation failed |
| 500 | Unexpected server error |

Actual responses depend on the exception handling implemented in each endpoint.

## Running Tests

You can test the API using Swagger UI, Postman, or `curl`.

Example:

```bash
curl http://127.0.0.1:8000/
```

For protected endpoints:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://127.0.0.1:8000/item
```

## Security Considerations

- Validate access tokens on every protected request.
- Verify resource ownership before updating or deleting items.
- Keep database credentials and JWT secrets in environment variables.
- Never expose internal database errors to API clients.
- Use HTTPS when deploying outside a trusted local environment.
- Apply appropriate token expiration and authorization policies.

## License

Add your preferred license here, such as MIT, if applicable.
