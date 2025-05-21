# LaTeX Compilation Service

This project provides a simple API service for compiling LaTeX documents into PDFs. It uses a FastAPI server and a pdflatex Docker image.

## Overview

The service consists of two main components orchestrated via `docker-compose.yml`:

1.  **`api` service**: A Python FastAPI application that exposes an endpoint to receive LaTeX source code. It then uses the `pdflatex` service to compile the document.
2.  **`pdflatex` service**: Runs the `cristiangreco/pdflatex` Docker image, which provides the TeX Live distribution.

A GitHub Actions CI workflow is included in `.github/workflows/ci.yml` to automatically build the services and test the compilation endpoint on pull requests.

## Prerequisites

-   Docker
-   Docker Compose

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Build and run the services:**
    ```bash
    docker-compose up --build -d
    ```
    The API service will be available on `http://localhost:8000`.

## API Usage

### Compile LaTeX Document

-   **Endpoint:** `/compile`
-   **Method:** `POST`
-   **Request Body:** JSON object with a `source` key containing the LaTeX document content.
    ```json
    {
      "source": "\documentclass{article}\begin{document}Hello, world!\end{document}"
    }
    ```
-   **Example with `curl`:**
    ```bash
    curl -X POST -H "Content-Type: application/json"     -d '{"source": "\documentclass{article}\begin{document}Hello from API!\end{document}"}'     -o output.pdf http://localhost:8000/compile
    ```
    This command will save the compiled PDF as `output.pdf`.

-   **Success Response:**
    -   Status Code: `200 OK`
    -   Content-Type: `application/pdf`
    -   Body: The compiled PDF document.

-   **Error Response:**
    -   Status Code: `400 Bad Request` (or other appropriate error codes)
    -   Content-Type: `application/json`
    -   Body: JSON object with an `error` key describing the issue.
      ```json
      {
        "error": "LaTeX compilation failed",
        "details": "<pdflatex command output>"
      }
      ```

## Testing

Unit tests for the API are located in `test_main.py` and can be run using `pytest` within the API container or a local environment with dependencies installed.

The CI workflow also performs an integration test using `curl`.
