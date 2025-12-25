# Инструкция по настройке базы данных и созданию администратора

## ⚠️ ВАЖНО: Администратор больше не создается автоматически в коде!

Администратор должен быть создан вручную в базе данных для безопасности.

---

## Простой способ (без sqlplus)

### Вариант 1: Использовать графический инструмент (DBeaver, SQL Developer, Oracle SQL Developer)

1. **Установите DBeaver** (бесплатный): https://dbeaver.io/download/
2. **Подключитесь к Oracle БД:**
   - Host: `localhost`
   - Port: `1521`
   - Database: `XE`
   - Username: `system`
   - Password: ваш пароль

3. **Выполните SQL скрипт** (см. ниже "Шаг 3: Создание администратора")

### Вариант 2: Использовать временный endpoint в приложении

Создайте временный контроллер для создания админа (см. раздел "Создание админа через API" ниже).

---

## Шаг 1: Очистка базы данных (опционально)

### Подключение к Oracle Database

**Если у вас установлен sqlplus:**
```bash
sqlplus system/your_password@localhost:1521/XE
```

**Если sqlplus не установлен, используйте DBeaver или другой графический инструмент.**

### SQL-скрипт для полной очистки БД

```sql
-- Отключить проверку внешних ключей
SET CONSTRAINTS ALL DEFERRED;

-- Удалить все данные из таблиц (в правильном порядке из-за внешних ключей)
DELETE FROM points;
DELETE FROM role_requests;
DELETE FROM user_roles;
DELETE FROM users;

-- Очистить последовательности (опционально, если нужно начать ID с 1)
-- ВНИМАНИЕ: Это сбросит счетчики ID!
DROP SEQUENCE user_seq;
DROP SEQUENCE point_seq;
DROP SEQUENCE role_request_seq;

CREATE SEQUENCE user_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE point_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE role_request_seq START WITH 1 INCREMENT BY 1;

-- Закоммитить изменения
COMMIT;
```

**Альтернативный вариант (только очистка данных, без сброса последовательностей):**

```sql
DELETE FROM points;
DELETE FROM role_requests;
DELETE FROM user_roles;
DELETE FROM users;
COMMIT;
```

---

## Шаг 2: Генерация BCrypt хеша пароля

### Самый простой способ: Онлайн-генератор

1. Перейдите на сайт: **https://bcrypt-generator.com/**
2. Введите желаемый пароль для админа
3. Нажмите "Generate Hash"
4. Скопируйте полученный хеш (например: `$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy`)

---

## Шаг 3: Создание администратора в базе данных

### Способ 1: Через SQL (DBeaver, SQL Developer, или другой инструмент)

**Выполните этот SQL скрипт в вашем инструменте для работы с БД:**

```sql
-- 1. Создать пользователя
-- ЗАМЕНИТЕ 'YOUR_BCRYPT_HASH_HERE' на хеш, полученный на шаге 2
INSERT INTO users (id, login, password_hash) 
VALUES (user_seq.NEXTVAL, 'admin', 'YOUR_BCRYPT_HASH_HERE');

-- 2. Добавить роль ADMIN
-- Используем подзапрос для получения ID только что созданного пользователя
INSERT INTO user_roles (user_id, role) 
SELECT id, 'ADMIN' FROM users WHERE login = 'admin';

-- 3. Проверить результат
SELECT u.id, u.login, ur.role 
FROM users u 
LEFT JOIN user_roles ur ON u.id = ur.user_id 
WHERE u.login = 'admin';

COMMIT;
```

**Пример с конкретным хешем:**
```sql
-- Хеш для пароля 'admin' (сгенерируйте свой через https://bcrypt-generator.com/)
INSERT INTO users (id, login, password_hash) 
VALUES (user_seq.NEXTVAL, 'admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy');

INSERT INTO user_roles (user_id, role) 
SELECT id, 'ADMIN' FROM users WHERE login = 'admin';

COMMIT;
```

### Способ 2: Создание админа через API (временный endpoint)

**⚠️ ВАЖНО: Этот способ менее безопасен, используйте только для разработки!**

1. Создайте временный контроллер `AdminSetupController.kt`:

```kotlin
package com.example.controller

import com.example.entity.Role
import com.example.service.UserService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/setup")
@CrossOrigin(originPatterns = ["*"])
class AdminSetupController(
    private val userService: UserService
) {
    @PostMapping("/admin")
    fun createAdmin(@RequestBody request: Map<String, String>): ResponseEntity<Map<String, Any>> {
        val login = request["login"] ?: "admin"
        val password = request["password"] ?: throw IllegalArgumentException("Пароль обязателен")
        
        val admin = userService.createUser(login, password, setOf(Role.ADMIN))
        
        return ResponseEntity.ok(mapOf(
            "message" to "Администратор создан",
            "login" to admin.login,
            "warning" to "⚠️ УДАЛИТЕ AdminSetupController после использования!"
        ))
    }
}
```

2. Добавьте endpoint в SecurityConfig (строка 39):
```kotlin
.requestMatchers("/api/auth/register", "/api/auth/login", "/api/health", "/api/setup/**").permitAll()
```

3. Создайте админа:
```bash
curl -X POST http://localhost:8080/api/setup/admin \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "your_secure_password"}'
```

4. **Удалите AdminSetupController после использования!**

---

## Шаг 4: Проверка

### Проверка через SQL

```sql
SELECT u.id, u.login, ur.role 
FROM users u 
LEFT JOIN user_roles ur ON u.id = ur.user_id 
ORDER BY u.id;
```

### Проверка через API

```bash
# Войдите как админ
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin",
    "password": "your_password"
  }'
```

Если все правильно, вы получите JWT токен.

---

## Рекомендации по безопасности

1. **Используйте сильный пароль** для администратора:
   - Минимум 12 символов
   - Комбинация букв (заглавных и строчных), цифр и специальных символов
   - Не используйте словарные слова

2. **Храните пароль безопасно**:
   - Не коммитьте пароль в Git
   - Используйте менеджер паролей
   - Не передавайте пароль по незащищенным каналам

3. **Регулярно меняйте пароль** администратора

4. **Ограничьте доступ** к базе данных:
   - Используйте сильные пароли для пользователей БД
   - Ограничьте сетевой доступ к БД

---

## Устранение проблем

### Ошибка: "ORA-00001: unique constraint violated"
**Причина:** Пользователь с таким логином уже существует  
**Решение:** Удалите существующего пользователя:
```sql
DELETE FROM user_roles WHERE user_id = (SELECT id FROM users WHERE login = 'admin');
DELETE FROM users WHERE login = 'admin';
COMMIT;
```

### Ошибка: "ORA-02291: integrity constraint violated"
**Причина:** Попытка вставить роль для несуществующего пользователя  
**Решение:** Убедитесь, что пользователь создан перед добавлением роли

### Не могу войти после создания админа
**Проверьте:**
1. Хеш пароля сгенерирован правильно (BCrypt)
2. Логин в БД совпадает с логином при входе
3. Пароль введен правильно (без лишних пробелов)
4. Приложение запущено и подключено к правильной БД

---

## Краткая инструкция (TL;DR)

1. **Сгенерируйте BCrypt хеш:** https://bcrypt-generator.com/
2. **Подключитесь к БД** через DBeaver или другой инструмент
3. **Выполните SQL:**
```sql
INSERT INTO users (id, login, password_hash) 
VALUES (user_seq.NEXTVAL, 'admin', 'ВАШ_BCRYPT_ХЕШ');

INSERT INTO user_roles (user_id, role) 
SELECT id, 'ADMIN' FROM users WHERE login = 'admin';

COMMIT;
```
4. **Проверьте вход** через `/api/auth/login`
