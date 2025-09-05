# Face Recognition API

Микросервис на **FastAPI** для оффлайн-сравнения лиц с использованием [DeepFace](https://github.com/serengil/deepface).

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Dimash0203/face_recognition.git
cd face_recognition
```

### 2. Установить зависимости
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Скачать веса моделей
Скачать из Google Drive → [weights](https://drive.google.com/drive/folders/1_DEIoTXIyLP3SvhsNLdoY2OyutUV1Sxo?usp=drive_link)  
и положить файлы `*.h5` в папку `./weights/`.

### 4. Настроить модели
В файле **models.txt** укажите, какие модели использовать:
```ini
Facenet    = True
Facenet512 = False
ArcFace    = False
```
По умолчанию включен только **Facenet**.

### 5. Запуск
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Документация API → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API эндпоинты

### `GET /models`  
Список активированных моделей (по данным `models.txt`).

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/models" -H "accept: application/json"
```
**Пример ответа:**
```json
[
  "Facenet"
]
```

---

### `POST /verify`  
Сравнение двух изображений (multipart/form-data).

**Параметры:**  
- `image1` — первое изображение (jpeg/png)  
- `image2` — второе изображение (jpeg/png)  

**Пример запроса:**
```bash
curl -X POST "http://127.0.0.1:8000/verify"   -H "accept: application/json"   -H "Content-Type: multipart/form-data"   -F "image1=@same2.jpeg;type=image/jpeg"   -F "image2=@same1.jpeg;type=image/jpeg"
```

**Пример ответа:**
```json
{
  "detector_backend": "retinaface",
  "threshold": 0.7,
  "results": [
    {
      "model": "Facenet",
      "lookalike_percent": 72,
      "same_person": true,
      "error": null
    }
  ]
}
```

---

### `POST /verify-b64`  
Сравнение изображений в **Base64** формате.

**Пример тела запроса:**
```json
{
  "image1_b64": "string",
  "image2_b64": "string"
}
```

**Пример ответа:**
```json
{
  "detector_backend": "retinaface",
  "threshold": 0.7,
  "results": [
    {
      "model": "Facenet",
      "lookalike_percent": 72,
      "same_person": true,
      "error": null
    }
  ]
}
```

---

### `GET /healthz`  
Проверка статуса сервиса.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/healthz" -H "accept: application/json"
```

**Пример ответа:**
```json
{
  "status": "ok",
  "app": "Face Verification API",
  "version": "1.0.0"
}
```

---

## ⚙️ Продакшен
```bash
gunicorn -c gunicorn_conf.py main:app
```