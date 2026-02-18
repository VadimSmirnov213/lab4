## Стек

- **Backend**: Kotlin, Spring Boot (Web, Security, Data JPA, Validation), Spring Security, JWT, Oracle Database
- **Frontend**: Vue 3, Vite, vue-router
- **Аутентификация**: JWT Bearer, BCrypt

## REST API

### Auth (публичные ручки)

- **POST** `/api/auth/register`  
  Body: `{ "login": "string", "password": "string" }`  
  Ответ: `AuthResponse { success, message, token }`

- **POST** `/api/auth/login`  
  Body: `{ "login": "string", "password": "string" }`  
  Ответ: `AuthResponse { success, message, token }`

### Points (нужен JWT в `Authorization: Bearer <token>`)

- **POST** `/api/check`  
  Проверка и сохранение точки.  
  Body (PointDto): `{ "x": number, "y": number, "r": number }`

- **GET** `/api/points`  
  Получить все точки текущего пользователя.

- **DELETE** `/api/points`  
  Удалить все точки текущего пользователя.

### Admin (роль `ADMIN`)

- **DELETE** `/api/admin/users/{login}`  
  Удалить пользователя по логину (нельзя удалить самого себя).

- **PATCH** `/api/admin/users/{login}/analyst`  
  Выдать пользователю роль `ANALYST`.

### Analytics (роль `ANALYST`)

- **GET** `/api/analytics/users`  
  Список пользователей с их ролями.

- **GET** `/api/analytics/users/{login}/statistics`  
  Статистика по точкам конкретного пользователя.
