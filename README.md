# Face Verification API (только Facenet)

Этот сервис реализует оффлайн‑сравнение лиц по фотографиям с использованием модели **Facenet**.

---

## Возможности

- Сравнение двух изображений (multipart/form-data или base64).
- Используется только модель **Facenet**.
- Поддержка watchdog:
  - Периодически выполняет смоук‑тест на эталонном фото.
  - Автоматически сбрасывает/перезагружает модели при сбоях.
- Админ‑эндпоинт для ручного сброса моделей.

---

## Структура проекта

```
face_recognition/
├── app/                # код приложения (API, сервис, утилиты)
├── weights/            # веса моделей (.h5)
├── logs/               # файлы логов
├── tests/              # тестовые изображения (для watchdog)
│   └── same.jpeg
├── .env                # конфигурация
├── main.py             # точка входа
├── requirements.txt
└── README.md
```

## API

### Проверка здоровья
```
GET /healthz
```
Ответ:
```json
{"status":"ok","app":"Face Verification API","version":"1.2.0"}
```

### Список моделей
```
GET /models
```
Ответ: `["Facenet"]`

### Сравнение изображений (multipart)
```
POST /verify?threshold=0.75
```
Формат: `multipart/form-data` с двумя файлами (`image1`, `image2`).

### Сравнение изображений (base64)
```
POST /verify-b64
```
Тело запроса:
```json
{
  "image1_b64": "data:image/jpeg;base64,...",
  "image2_b64": "data:image/jpeg;base64,...",
  "threshold": 0.8
}
```

### Ручной сброс моделей
```
POST /admin/reload
```
Ответ:
```json
{"status":"ok","message":"Модели перезагружены"}
```

---

## Логирование

- Все логи пишутся в `logs/app.txt`.
- Уровень логирования задаётся переменной `LOG_LEVEL` (по умолчанию INFO).

---

## Ошибки

- Если лицо не найдено:
  ```json
  {"model":"Facenet","error":"Лицо не обнаружено на изображении 1..."}
  ```
- Если произошла внутренняя ошибка: пользователю короткое сообщение, в логах — полная трассировка.

---

## Watchdog

- Каждые `WATCHDOG_INTERVAL_SEC` секунд запускается смоук‑тест на файле `SMOKETEST_IMAGE_PATH`.
- Если тест не пройден, автоматически выполняется `reset_models()` и прогружается Facenet заново.
- Можно отключить в `.env`:
  ```env
  WATCHDOG_ENABLED=false
  ```

---

## Пример использования

```bash
curl -X POST "http://localhost:8000/verify?threshold=0.8"   -F "image1=@tests/same1.jpeg"   -F "image2=@tests/same1.jpeg"
```

Ответ:
```json
{
  "detector_backend": "opencv",
  "threshold": 0.8,
  "results": [
    {"model":"Facenet","lookalike_percent":100,"same_person":true}
  ]
}
```
