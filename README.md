# 🐳 Backend Patent Analyzer (Dockerized)

## 📦 Run the Docker Container

Ensure you have **Docker** and **Docker Compose** installed on your machine. You can install Docker from the [official Docker documentation](https://docs.docker.com/get-docker/).

### Steps:

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd frontend
   ```

2. **Build and start the Docker containers**:
   This will pull the necessary images and organize them to run the services specified in the `docker-compose.yml` file.

   ```bash
   docker pull holyknight101/backend_patent-analyzer_v1:latest
   docker-compose up --build

   for windows use, replace this line in package.json: 
   (macOs)
   "backend": "docker stop selenium-firefox backend || true && docker rm selenium-firefox backend || true && docker-compose up --build",
   into 
   (windows)
   "backend": "docker stop selenium-firefox backend && docker rm selenium-firefox backend && docker-compose up --build",

   npm i
   npm run dev
   ```

### App will be available at:

👉 [http://localhost:8000](http://localhost:8000)

---

## 📤 Upload a PDF File

To upload a patent document (PDF), you can use the following command with `curl`. Make sure to replace `/path/to/your/file.pdf` with the actual path to the PDF file on your system.

```bash
curl -X POST -F "file=@/path/to/your/file.pdf" http://localhost:8000/upload
```

---

## 📤 Enable Chatbot Conversation

You can send queries to the backend using this `curl` command to interact with the chatbot. Here’s an example to ask about the patent:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the patent about?"}'
```

---

## 🛑 Stop & Clean Up

To stop and remove the Docker containers, run the following commands:

1. **Stop the containers**:

   ```bash
   docker-compose down
   docker image prune -f
   ```
---

## 💡 Works on x64 Architecture

This setup is designed to work seamlessly on **Linux**, **Windows** (with Docker Desktop), and **macOS** (including Intel & Apple Silicon-based systems).

For **x64 architecture** (Intel and AMD processors), Docker and Docker Compose are supported out of the box. Just ensure you have the correct Docker images and dependencies for the architecture, which Docker handles automatically.

Cons: require a lot of memory and storage

Run frontend
