# Computer Vision Bot

**CV Bot** is a lightweight assistant for computer vision projects.  
It provides basic tools to manage cameras, run inference, handle model weights, and prepare datasets for training.

---

## 🚀 Features (v1)

- **Cameras**
  - Check camera availability
  - Capture snapshots

- **Weights (YOLO only)**
  - Add YOLO weights
  - Use weights for inference and testing

- **Recording**
  - Record video streams from cameras

- **Inference Recording**
  - Run YOLO inference on video streams
  - Save inference results

- **Training**
  - Collect datasets for future model training

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Zzior/cv_bot.git
cd cv_bot
````

### 2. Configure environment variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env
```

Example `.env` configuration:

```dotenv
DEFAULT_LANGUAGE="en"  # currently only English is supported
TIME_ZONE="UTC"

# If you are using Docker, do not edit Postgres configs
POSTGRES_DB="cv_bot"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_PORT="5432"
POSTGRES_HOST="cv_bot_db"

BOT_TOKEN="your-telegram-bot-token"
USER_IDS="1111111111 2222222222"
LOG_CHAT_ID="100"
```

---

## ⚙️ Optional: Override Docker Compose

If you need custom volume mappings or ports, create or edit `compose.override.yaml`:

```bash
nano compose.override.yaml
```

Example override configuration:

```yaml
services:
  cv_bot:
    volumes: !override
      - ./:/app
      - /mnt/hdd/cv_bot:/app/storage

  cv_bot_fb:
    volumes: !override
      - /mnt/hdd/cv_bot:/srv
      - ./docker_storage/filebrowser:/database
    ports: !override
      - "7000:8080"
```

---

## 🐳 Build and Run with Docker

```bash
sudo docker compose build
sudo docker compose up -d
```

The bot should now be up and running in detached mode.

---

## 📌 Notes

* Only **YOLO-based models** are currently supported.
* Make sure your cameras are accessible from the Docker container.
