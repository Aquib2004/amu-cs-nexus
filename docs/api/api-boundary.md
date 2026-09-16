# AMUCS Nexus - API Boundary

> TARGET DESIGN - only /api/health is implemented so far.

## What an API boundary is

The API boundary is the contract between the frontend and the backend. It defines exactly which operations the backend exposes and how clients call them. Everything behind the boundary (application logic, database, AI) is an implementation detail hidden from the client.

## HTTP / REST primer (learning)

| Concept | Meaning |
|---------|---------|
| Client | The program making a request (the Next.js frontend, or `requests` in Python). |
| Server | The program responding (FastAPI). |
| Request | The client asking the server for something. |
| Response | The server result, including a status code and body. |
| URL | The address of a resource, e.g. `https://host/api/notices/42`. |
| Method | The intended action: GET, POST, PUT, PATCH, DELETE. |
| Headers | Metadata about the request/response (content type, auth). |
| Query parameters | `?key=value` appended to a URL; used for optional filters. |
| Path parameters | Values embedded in the URL path, e.g. `/api/documents/{id}`. |
| Request body | Data sent with some methods (JSON for POST/PUT). |
| JSON | The data format the API uses for bodies (key/value text). |
| Status code | The outcome of the request (200 ok, 404 not found, 422 validation). |
| Validation | Checking request data against rules before use. |
| Errors | Structured problem responses when something fails. |
| HTTPS | HTTP encrypted with TLS, so data is safe in transit. |

With Python requests, a GET with query parameters looks like:

```python
import requests
response = requests.get("http://localhost:8000/api/search", params={"q": "computer vision"})
response.raise_for_status()  # raise on 4xx/5xx
results = response.json()     # parse JSON body
```

## Planned endpoints (not implemented yet)

The final set should include:

| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/health | service status |
| GET | /api/notices | list/filter notices |
| GET | /api/notices/{id} | a single notice |
| GET | /api/documents/{id} | a single document |
| GET | /api/faculty | list faculty |
| GET | /api/search | search documents/content |
| POST | /api/chat | ask a question, get answer + citations |
| POST | /api/feedback | submit feedback |

We will implement these one at a time and teach the HTTP semantics of each (method, query params, path params, body, status codes, validation, errors).

## API design principles

- **REST:** expose resources (notices, documents, faculty) with meaningful verbs and URLs.
- **Explicit validation:** every request is validated before use; invalid input returns 422 with a structured error.
- **Secure by default:** HTTPS, CORS configured later, rate limiting and safe logging when those phases arrive.
- **Source-grounded:** search and chat results carry source URLs so answers are verifiable.

