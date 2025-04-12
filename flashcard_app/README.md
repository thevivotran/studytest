# Flashcard Web Application

A simple web application built with Flask and SQLite to help users study flashcards from custom datasets imported via CSV files. The application is designed to be run locally using Docker or Podman.

## Features

*   Import flashcard datasets from CSV files.
*   View flashcards one by one.
*   Click to reveal the answer.
*   Navigate between cards (Next/Previous).
*   Progress is saved per dataset.
*   Persistent storage for database and progress using Docker volumes.

## Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) or [Podman](https://podman.io/getting-started/installation) installed.

## CSV File Format

The application expects a CSV file with **no header row** and either 6 or 7 columns in the following order:

1.  `question` (Text) - The question text for the flashcard.
2.  `correct_answer` (Text) - The correct answer to the question.
3.  `choice1` (Text) - The first answer choice.
4.  `choice2` (Text) - The second answer choice.
5.  `choice3` (Text) - The third answer choice.
6.  `choice4` (Text) - The fourth answer choice.
7.  `choice5` (Text, Optional) - The fifth answer choice (can be empty or omitted).

*   Ensure the file is encoded in **UTF-8**.
*   Required fields (question, correct_answer, choices 1-4) must not be empty.

**Example Row (6 columns):**
`"What is 2+2?","4","Two","Three","Four","Five"`

**Example Row (7 columns):**
`"Capital of France?","Paris","London","Berlin","Paris","Madrid","Rome"`

## Build Instructions

Navigate to the directory containing the `Dockerfile` (the `flashcard_app` directory) and run:

**Using Docker:**
```bash
docker build -t flashcard-app .
```

**Using Podman:**
```bash
podman build -t flashcard-app .
```

## Run Instructions

To run the application, you need to map a local directory to the container's `/data` volume for persistent storage of the database (`flashcard.db`) and progress (`progress.json`).

1.  **Create a local directory** to store the persistent data (e.g., `my_flashcard_data` in your home directory or project space). Make sure this directory exists before running the container.
    ```bash
    mkdir ~/my_flashcard_data
    ```
    *(Adjust the path `~/my_flashcard_data` as needed)*

2.  **Run the container:**

    **Using Docker:**
    ```bash
    docker run -p 5000:5000 -v ~/my_flashcard_data:/data --name flashcard-instance flashcard-app
    ```
    *   `-p 5000:5000`: Maps port 5000 on your host to port 5000 in the container.
    *   `-v ~/my_flashcard_data:/data`: Mounts your local `my_flashcard_data` directory to `/data` inside the container. **Replace `~/my_flashcard_data` with the actual path to the directory you created.**
    *   `--name flashcard-instance`: Assigns a name to the running container for easier management (optional).
    *   `flashcard-app`: The name of the image you built.

    **Using Podman:**
    ```bash
    podman run -p 5000:5000 -v ~/my_flashcard_data:/data:Z --name flashcard-instance localhost/flashcard-app
    ```
    *   Parameters are similar to Docker.
    *   `:Z` is often needed with Podman on SELinux systems to handle volume permissions correctly.
    *   `localhost/flashcard-app`: Podman often prefixes local image names with `localhost/`.

3.  **Access the application:** Open your web browser and navigate to `http://localhost:5000`.

## Stopping the Container

**Using Docker:**
```bash
docker stop flashcard-instance
docker rm flashcard-instance # Optional: remove the container if you don't need it anymore
```

**Using Podman:**
```bash
podman stop flashcard-instance
podman rm flashcard-instance # Optional: remove the container
```

Your data in `~/my_flashcard_data` will persist even after stopping/removing the container.