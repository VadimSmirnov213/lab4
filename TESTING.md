# Инструкция по тестированию API

## Важная информация

- **Админ жестко зашит в коде** - пользователь с логином `admin` и паролем `admin` создается автоматически при запуске приложения
- **При регистрации все пользователи получают роль USER** - нельзя зарегистрироваться как админ или аналитик
- **Роль аналитика** можно получить только через запрос админу

---

## Подготовка

### 1. Получение JWT токена

#### Регистрация нового пользователя (автоматически получает роль USER):
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user1",
    "password": "password123"
  }'
```

#### Вход в систему:
```bash
# Вход как админ (создается автоматически)
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin",
    "password": "admin"
  }'

# Вход как обычный пользователь
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user1",
    "password": "password123"
  }'
```

**Ответ содержит токен:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "login": "user1",
  "roles": ["USER"]
}
```

**Сохраните токен в переменную для удобства:**
```bash
TOKEN="ваш_токен_здесь"
```

---

## Базовые эндпоинты (доступны всем аутентифицированным пользователям)

### 1. Проверить точку
```bash
curl -X POST http://localhost:8080/api/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "x": 1.5,
    "y": 2.0,
    "r": 3.0
  }'
```

**Ответ:**
```json
{
  "x": 1.5,
  "y": 2.0,
  "r": 3.0,
  "hit": true
}
```

### 2. Получить все точки пользователя
```bash
curl -X GET http://localhost:8080/api/points \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
[
  {
    "x": 1.5,
    "y": 2.0,
    "r": 3.0,
    "hit": true
  },
  {
    "x": -1.0,
    "y": -1.0,
    "r": 2.0,
    "hit": false
  }
]
```

### 3. Удалить все точки пользователя
```bash
curl -X DELETE http://localhost:8080/api/points \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
  "message": "Точки удалены"
}
```

---

## Дополнительные эндпоинты

### 1. Назначить пользователя аналитиком по логину (ADMIN)

Админ может назначить роль ANALYST любому пользователю по его логину:

```bash
curl -X PATCH http://localhost:8080/api/admin/users/user1/analyst \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
  "id": 2,
  "login": "user1",
  "roles": ["USER", "ANALYST"],
  "message": "Роль ANALYST назначена пользователю"
}
```

**Примечание:** Роль ANALYST добавляется к существующим ролям пользователя.

### 2. Посмотреть список пользователей (ANALYST)

Аналитик может получить список всех пользователей:

```bash
curl -X GET http://localhost:8080/api/analytics/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
[
  {
    "id": 1,
    "login": "admin",
    "roles": ["ADMIN"]
  },
  {
    "id": 2,
    "login": "user1",
    "roles": ["USER"]
  },
  {
    "id": 3,
    "login": "analyst1",
    "roles": ["ANALYST"]
  }
]
```

### 3. Посмотреть статистику попаданий пользователя по логину (ANALYST)

Аналитик может получить статистику попаданий для любого пользователя по его логину:

```bash
curl -X GET http://localhost:8080/api/analytics/users/user1/statistics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
  "userId": 2,
  "login": "user1",
  "totalPoints": 10,
  "hitPoints": 5,
  "hitPercentage": 50.0
}
```

**Поля ответа:**
- `userId` - ID пользователя
- `login` - логин пользователя
- `totalPoints` - общее количество точек
- `hitPoints` - количество попаданий
- `hitPercentage` - процент попаданий

### 4. Удалить пользователя по логину (ADMIN)

Админ может удалить любого пользователя по его логину:

```bash
curl -X DELETE http://localhost:8080/api/admin/users/user1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
  "message": "Пользователь удален"
}
```

**Примечание:** Админ не может удалить самого себя.

---

## Тестирование сценариев

### Сценарий 1: Админ назначает пользователя аналитиком

```bash
# 1. Вход как админ
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"admin"}' | jq -r '.token')

# 2. Назначить пользователя аналитиком
curl -X PATCH http://localhost:8080/api/admin/users/user1/analyst \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### Сценарий 2: Аналитик просматривает статистику

```bash
# 1. Вход как аналитик (после одобрения запроса админом)
ANALYST_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"analyst1","password":"analyst123"}' | jq -r '.token')

# 2. Получить список всех пользователей
curl -X GET http://localhost:8080/api/analytics/users \
  -H "Authorization: Bearer $ANALYST_TOKEN"

# 3. Получить статистику конкретного пользователя
curl -X GET http://localhost:8080/api/analytics/users/user1/statistics \
  -H "Authorization: Bearer $ANALYST_TOKEN"
```

### Сценарий 3: Админ удаляет пользователя

```bash
# 1. Вход как админ
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"admin"}' | jq -r '.token')

# 2. Удалить пользователя по логину
curl -X DELETE http://localhost:8080/api/admin/users/user1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Тестирование ошибок доступа

### Попытка доступа без токена (должна вернуть 403):
```bash
curl -X GET http://localhost:8080/api/points \
  -H "Content-Type: application/json"
```

### Попытка доступа с токеном USER к аналитическим эндпоинтам (должна вернуть 403):
```bash
curl -X GET http://localhost:8080/api/analytics/users \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json"
```

### Попытка доступа с токеном USER к админским эндпоинтам (должна вернуть 403):
```bash
curl -X DELETE http://localhost:8080/api/admin/users/user1 \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json"
```

### Попытка админа удалить самого себя (должна вернуть ошибку):
```bash
curl -X DELETE http://localhost:8080/api/admin/users/admin \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Полезные команды

### Проверка текущей аутентификации:
```bash
curl -X GET http://localhost:8080/api/auth/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Ответ при успешной аутентификации:**
```json
{
  "authenticated": true,
  "login": "user1"
}
```

### Проверка здоровья API:
```bash
curl -X GET http://localhost:8080/api/health \
  -H "Content-Type: application/json"
```

**Ответ:**
```json
{
  "status": "ok"
}
```

---

## Примечания

- Все запросы требуют JWT токен в заголовке `Authorization: Bearer <token>`
- Токен выдается при успешном входе через `/api/auth/login`
- Роли проверяются через `@PreAuthorize` аннотации
- Админ, аналитик и пользователь имеют доступ ко всем эндпоинтам для работы с точками (`/api/points`, `/api/check`)
- Админ не может удалить самого себя
- При регистрации все пользователи автоматически получают роль USER
