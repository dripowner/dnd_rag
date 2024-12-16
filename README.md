# DnD-Assistant

## Описание

RAG ассистент, который использует Mistral AI для ответов на вопросы о правилах DnD.

## Как запустить

Скопируйте файл `.env.example` в `.env` и заполните его:
- `MISTRAL_API_KEY` - ключ API Mistral AI
- `HOST` - хост, на котором будет запущен FastAPI
- `PORT` - порт, на котором будет запущен FastAPI

windows + wsl2 / linux:
- `make up` - запуск приложения
- `make build` - сборка приложения
- `make down` - завершение работы приложения

