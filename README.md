# AI-Powered Blood Test Report Analyzer

This project is a sophisticated, AI-powered application designed to analyze blood test reports from PDF files. It extracts data, provides insights on nutrition and exercise, and ensures the security of sensitive information through encryption. The system is built with a scalable architecture using FastAPI for the API, Celery for asynchronous task processing, and CrewAI for orchestrating AI agents.

## Features

-   **PDF Blood Report Analysis:** Upload a blood test report in PDF format for automated analysis.
-   **AI-Powered Insights:** Leverages multiple AI agents to interpret the report, offering general guidance on nutrition and exercise.
-   **Asynchronous Processing:** Uses Celery and Redis to handle analysis tasks in the background, ensuring the API remains responsive.
-   **Secure by Design:** Encrypts uploaded PDF files to protect sensitive health information.
-   **Flexible LLM Configuration:** Supports both local LLMs (via Ollama) and OpenAI models, with easy configuration switching.
-   **Status Tracking:** Provides an endpoint to check the status of an analysis task.
-   **Database Integration:** Stores analysis results in a database for persistence.
-   **Vector Store:** Utilizes a FAISS vector store for efficient similarity search on report embeddings.
-   **Interactive API Documentation:** Automatically generated, interactive API documentation via Swagger UI.
-   **Task Monitoring:** Includes support for Flower, a real-time monitoring tool for Celery.

## System Architecture

The application consists of three main components:

1.  **FastAPI Web Server:** Provides the API endpoints for uploading files and checking task status. It handles incoming requests, validates them, and dispatches analysis tasks to the Celery queue.
2.  **Celery Worker:** A background worker that consumes tasks from the queue. It performs the heavy lifting of decrypting the file, analyzing the content with AI agents, and storing the results.
3.  **Redis:** Acts as both the message broker for Celery (to queue tasks) and the result backend (to store task outcomes).

The AI analysis is performed by a "crew" of agents, each with a specific role:
-   **Verifier Agent:** Checks if the uploaded document appears to be a valid medical report.
-   **Medical Report Analyst:** Interprets the blood test results to provide general insights.
-   **Nutrition Advisor:** Offers dietary suggestions based on the report.
-   **Fitness Coach:** Recommends physical activities tailored to the health indicators.

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

-   Python 3.10+
-   [Redis](https://redis.io/topics/quickstart)
-   [Ollama](https://ollama.ai/) for running the local LLM. Ensure you have pulled the `mistral` model:
    ```bash
    ollama pull mistral
    ```

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the project root by copying the example.
    ```bash
    cp .env.example .env
    ```
    The default `.env` is configured for the local Ollama setup.

### Running the Application

You need to run three separate services: the Redis server, the FastAPI application, and the Celery worker.

1.  **Start Redis:**

    **Option 1: Using Docker (Recommended)**

    If you have Docker installed, you can easily start a Redis container:

    ```bash
    docker run -d -p 6379:6379 --name blood-test-analyzer-redis redis:latest
    ```

    This command will download the latest Redis image, start a container in detached mode (`-d`), and map the container's port 6379 to the same port on your local machine.

    **Option 2: Local Installation**

    If you have Redis installed locally, run:
    ```bash
    redis-server
    ```

2.  **Start the Celery Worker:**
    Open a new terminal and run:
    ```bash
    celery -A celery_app.celery_app worker --loglevel=info
    ```

3.  **Start the FastAPI Server:**
    In another terminal, run:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Interactive Documentation

FastAPI provides automatically generated API documentation. Once the server is running, you can access the interactive Swagger UI at:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

This interface allows you to explore and test the API endpoints directly from your browser.

### 1. Analyze Blood Report

-   **URL:** `/analyze`
-   **Method:** `POST`
-   **Description:** Uploads a PDF blood test report for analysis.
-   **Form Data:**
    -   `file`: The PDF file to analyze.
    -   `query` (optional): A specific question or instruction for the analysis. Defaults to "Summarize my blood test report".
-   **Success Response (200):**
    ```json
    {
      "status": "queued",
      "task_id": "...",
      "analysis_id": "...",
      "file_processed": "report.pdf",
      "query": "Summarize my blood test report"
    }
    ```

### 2. Get Task Status

-   **URL:** `/status/{task_id}`
-   **Method:** `GET`
-   **Description:** Retrieves the status and result of an analysis task.
-   **Success Response (200):**
    -   If pending:
        ```json
        {
          "task_id": "...",
          "status": "PENDING"
        }
        ```
    -   If successful:
        ```json
        {
          "task_id": "...",
          "status": "SUCCESS",
          "result": "..."
        }
        ```

## LLM Configuration

This application is configured to use a local LLM by default, but can be easily switched to use OpenAI's API.

### Default: Local LLM with Ollama

The default configuration uses the `mistral` model running on a local Ollama instance.

-   **File to check:** `agents.py`
-   **Configuration:** The `llm` object is initialized with `ChatOllama`.
    ```python
    # agents.py
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="ollama/mistral", temperature=0.3)
    ```
-   **Environment Variables (`.env`):**
    ```
    OLLAMA_MODEL="ollama/mistral"
    OLLAMA_BASE_URL="http://localhost:11434"
    ```

### Switching to OpenAI

To use an OpenAI model like GPT-4, follow these steps:

1.  **Install the OpenAI library:**
    ```bash
    pip install langchain-openai
    ```

2.  **Update Environment Variables:**
    In your `.env` file, add your OpenAI API key and desired model name.
    ```
    # .env
    OPENAI_API_KEY="your_openai_api_key_here"
    OPENAI_MODEL_NAME="gpt-4-turbo"
    ```

3.  **Modify `agents.py`:**
    Comment out the `ChatOllama` initialization and uncomment/add the `ChatOpenAI` initialization.

    ```python
    # agents.py
    import os
    from dotenv import load_dotenv
    # from langchain_ollama import ChatOllama # Comment out
    from langchain_openai import ChatOpenAI # Add this import

    load_dotenv()

    # ... (tools remain the same) ...

    # --- LLM Configuration ---

    # Comment out the Ollama LLM
    # llm = ChatOllama(model="ollama/mistral", temperature=0.3)

    # Uncomment or add the OpenAI LLM
    llm = ChatOpenAI(
        model_name=os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # ... (the rest of the agent definitions) ...
    ```

4.  **Restart the Celery worker and FastAPI server** for the changes to take effect.

## In-Depth Components

### Database

The application uses a database to store the results of the blood test analyses.

-   **Technology:** By default, it uses SQLite, which is a serverless, file-based database. This is convenient for development and portability. The database file is `blood_analysis.db`.
-   **Schema:** The database contains a table (likely named `analysis_results` or similar) that stores information such as the analysis ID, the original query, the final report, and timestamps.
-   **ORM:** SQLAlchemy is used as the Object-Relational Mapper (ORM) to interact with the database. This allows the application to work with database records as Python objects.
-   **Production Use:** For a production environment, it is highly recommended to switch from SQLite to a more robust database like PostgreSQL. This would involve updating the `DATABASE_URL` in the `.env` file and ensuring the appropriate database driver (e.g., `psycopg2-binary`) is installed.

### Vector Store with FAISS

The application includes a vector store using FAISS (Facebook AI Similarity Search) for handling embeddings.

-   **Technology:** FAISS is a library for efficient similarity search and clustering of dense vectors. It is used here to create a simple, in-memory vector store.
-   **Functionality:** The `vector_store` directory contains the FAISS index. This allows the application to perform similarity searches on the embeddings of the blood test reports, which can be useful for finding similar reports or for other advanced features.
-   **Limitations:** This is a provisional setup and may not be suitable for a production environment. For a more robust solution, consider using a dedicated vector database like Pinecone or Weaviate.

### Celery and Task Queuing

Celery is used to manage a distributed task queue, which is essential for offloading the time-consuming AI analysis from the web server.

-   **Broker:** Redis serves as the broker, which is responsible for receiving tasks from the FastAPI server and passing them to the Celery workers.
-   **Backend:** Redis is also used as the result backend, storing the state and results of the tasks.
-   **Scalability:** You can scale the processing capacity by running more Celery workers, even on different machines.
-   **Limitations:**
    -   **Task Serialization:** By default, Celery uses `json` for serialization. This means that only JSON-serializable data can be passed as arguments to tasks and returned as results.
    -   **No Task Prioritization (by default):** In the default setup, tasks are processed in the order they are received (FIFO). For more advanced use cases, you might need to configure message priorities.

### Monitoring with Flower

Flower is a web-based tool for monitoring and administering Celery clusters.

-   **Installation:** Flower is already included in the `requirements.txt`.
-   **Running Flower:** To start the Flower dashboard, run the following command in a new terminal:
    ```bash
    celery -A celery_app.celery_app flower --broker=redis://localhost:6379/0
    ```
-   **Accessing the Dashboard:** The Flower dashboard will be available at `http://localhost:5555`.
-   **Features:**
    -   Real-time monitoring of tasks and workers.
    -   Ability to inspect task details, including arguments, return values, and tracebacks.
    -   Remote control of workers (e.g., revoking tasks, shutting down workers).

## Project Structure

```
.
├── agents.py           # Defines the CrewAI agents and tools
├── celery_app.py       # Celery application instance
├── database.py         # Database setup and session management
├── main.py             # FastAPI application and endpoints
├── requirements.txt    # Project dependencies
├── task.py             # Defines the main analysis task logic
├── tools.py            # Tools used by the agents
├── worker_tasks.py     # Celery task definitions
├── util/
│   └── crypto.py       # Encryption and decryption utilities
└── ...
```

## Security

All uploaded PDF files are encrypted using the Fernet symmetric encryption scheme from the `cryptography` library before being stored. The encryption key is read from a `secret.key` file, which should be generated once and kept secure.

To generate a key:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)
```