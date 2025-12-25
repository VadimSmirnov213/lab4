# Lab 4 - Web Programming

Веб-приложение для проверки попадания точек в заданную область на координатной плоскости.

## Технологии

### Backend
- **Spring Boot 4.0** (Kotlin)
- **Spring Data JPA** (Hibernate)
- **Spring Security**
- **Oracle Database**

### Frontend
- **Vue.js 3**
- **Vue Router**
- **Vite**

## Структура проекта

```
demo/
├── src/main/kotlin/com/example/  # Backend (Spring Boot)
│   ├── controller/               # REST API контроллеры
│   ├── service/                  # Бизнес-логика
│   ├── repository/               # Доступ к данным
│   ├── entity/                   # JPA Entity
│   ├── dto/                      # Data Transfer Objects
│   ├── mapper/                   # Преобразование Entity ↔ DTO
│   ├── validation/               # Валидация данных
│   ├── exception/                # Обработка исключений
│   └── config/                   # Конфигурация
└── frontend/                     # Frontend (Vue.js)
    └── src/
        ├── components/           # Vue компоненты
        ├── router.js             # Маршрутизация
        └── main.js               # Точка входа
```

## Запуск проекта

### Backend

1. Убедитесь, что Oracle Database запущена
2. Настройте `src/main/resources/application.properties`:
   ```properties
   spring.datasource.url=jdbc:oracle:thin:@localhost:1521:XE
   spring.datasource.username=system
   spring.datasource.password=your_password
   ```
3. Запустите:
   ```bash
   ./gradlew bootRun
   ```
   Backend будет доступен на `http://localhost:8080`

### Frontend

1. Перейдите в папку frontend:
   ```bash
   cd frontend
   ```
2. Установите зависимости:
   ```bash
   npm install
   ```
3. Запустите dev-сервер:
   ```bash
   npm run dev
   ```
   Frontend будет доступен на `http://localhost:3000`

## Тестовый пользователь

При первом запуске автоматически создается пользователь:
- **Логин:** `user`
- **Пароль:** `123`

## API Endpoints

### Авторизация
- `POST /api/auth/login` - Вход
- `POST /api/auth/logout` - Выход
- `GET /api/auth/check` - Проверка авторизации

### Точки
- `POST /api/check` - Проверка точки
- `GET /api/points` - Получить все точки пользователя
- `DELETE /api/points` - Удалить все точки пользователя
- `GET /api/health` - Health check

## Автор

Смирнов Вадим Константинович, Р3219
