# Анализ кода на избыточность

## 🔴 Критические избыточности

### 1. **JwtAuthenticationFilter - двойная загрузка пользователя**

**Проблема:** Загружаете пользователя дважды - через `authService.getCurrentUser()` и через `userDetailsService.loadUserByUsername()`

```kotlin
// Строки 34 и 36 в JwtAuthenticationFilter.kt
val user = authService.getCurrentUser(token)  // Запрос 1 к БД
val userDetails = userDetailsService.loadUserByUsername(login)  // Запрос 2 к БД
```

**Решение:** Используйте только `user`, authorities можно получить из `user.roles`:

```kotlin
val user = authService.getCurrentUser(token)
val authorities = user.roles.map { SimpleGrantedAuthority("ROLE_${it.name}") }

val authentication = UsernamePasswordAuthenticationToken(
    user,
    null,
    authorities
)
```

**Эффект:** Уменьшение количества запросов к БД с 2 до 1 на каждый запрос.

---

### 2. **AuthService - методы-прокси**

**Проблема:** Методы просто проксируют вызовы к `jwtService`:

```kotlin
// Строки 54-64 в AuthService.kt
fun validateToken(token: String): Boolean {
    return jwtService.validateToken(token)  // Просто прокси
}

fun getUserIdFromToken(token: String): Long {
    return jwtService.getUserIdFromToken(token)  // Просто прокси
}

fun getLoginFromToken(token: String): String {
    return jwtService.getLoginFromToken(token)  // Просто прокси
}
```

**Решение:** Используйте `jwtService` напрямую в `JwtAuthenticationFilter`:

```kotlin
// В JwtAuthenticationFilter
private val jwtService: JwtService  // Вместо authService

// Использование:
if (jwtService.validateToken(token)) {
    val login = jwtService.getLoginFromToken(token)
    // ...
}
```

**Эффект:** Упрощение архитектуры, меньше слоев абстракции.

---

### 3. **SecurityConfig - неиспользуемый corsFilter bean**

**Проблема:** Создается `corsFilter()` bean (строка 61-64), но он нигде не используется:

```kotlin
@Bean
fun corsFilter(): CorsFilter {
    return CorsFilter(corsConfigurationSource())  // Создается, но не используется
}
```

CORS уже настроен через `corsConfigurationSource()` в `securityFilterChain` (строка 34).

**Решение:** Удалите метод `corsFilter()`.

**Эффект:** Меньше неиспользуемого кода.

---

## 🟡 Средние избыточности

### 4. **@CrossOrigin на каждом контроллере**

**Проблема:** CORS уже настроен глобально в `SecurityConfig`, но каждый контроллер дублирует:

```kotlin
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class PointController(...)
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AdminController(...)
// и т.д.
```

**Решение:** Удалите `@CrossOrigin` из всех контроллеров, оставьте только глобальную настройку.

**Эффект:** Меньше дублирования, проще поддерживать.

---

### 5. **UserService.hashPassword - избыточный requireNotNull**

**Проблема:** `passwordEncoder.encode()` никогда не возвращает `null`:

```kotlin
fun hashPassword(password: String): String {
    return requireNotNull(passwordEncoder.encode(password)) { "Password encoding failed" }
}
```

**Решение:**
```kotlin
fun hashPassword(password: String): String {
    return passwordEncoder.encode(password)
}
```

**Эффект:** Меньше избыточного кода.

---

### 6. **UserService.deleteUser - избыточная проверка**

**Проблема:** Проверка `existsById` перед удалением избыточна:

```kotlin
fun deleteUser(userId: Long) {
    if (!userRepository.existsById(userId)) {  // Лишний запрос к БД
        throw com.example.exception.UserNotFoundException("Пользователь не найден")
    }
    userRepository.deleteById(userId)
}
```

**Решение:** `deleteById` сам выбросит исключение, если не найден. Или используйте `findById` и удаляйте:

```kotlin
fun deleteUser(userId: Long) {
    val user = userRepository.findById(userId)
        .orElseThrow { UserNotFoundException("Пользователь не найден") }
    userRepository.delete(user)
}
```

**Эффект:** Меньше запросов к БД.

---

### 7. **AuthService.getCurrentUser - двойная валидация токена**

**Проблема:** Токен уже проверен в фильтре, но проверяется еще раз:

```kotlin
// В JwtAuthenticationFilter (строка 31)
if (authService.validateToken(token)) {  // Проверка 1
    val user = authService.getCurrentUser(token)  // Внутри еще проверка (строка 41)
}

// В AuthService.getCurrentUser (строка 41)
if (!jwtService.validateToken(token)) {  // Проверка 2 - избыточно
    throw UnauthorizedException("Недействительный токен")
}
```

**Решение:** Уберите проверку из `getCurrentUser`, она уже есть в фильтре.

**Эффект:** Меньше избыточных проверок.

---

## 🟢 Мелкие замечания

### 8. **RoleRequestController - возможно неиспользуемый**

**Проблема:** Остался только метод `/my` для просмотра своих запросов. Если эта функциональность не используется, можно удалить.

**Решение:** Удалите, если не используется.

---

### 9. **UserService.updateUserRoles - не используется**

**Проблема:** Метод `updateUserRoles(userId, roles)` определен, но нигде не используется (используется только `assignAnalystRoleByLogin`).

**Решение:** Удалите, если не планируется использовать.

---

## 📊 Итоговая оценка

### Что нужно исправить обязательно:
1. ✅ Убрать двойную загрузку пользователя в `JwtAuthenticationFilter`
2. ✅ Удалить неиспользуемый `corsFilter()` bean
3. ✅ Убрать методы-прокси из `AuthService` или использовать `jwtService` напрямую

### Что желательно исправить:
4. ✅ Убрать `@CrossOrigin` из контроллеров
5. ✅ Упростить `hashPassword` и `deleteUser`
6. ✅ Убрать двойную валидацию токена

### Что можно оставить (если используется):
7. ⚠️ `RoleRequestController` - если функциональность нужна
8. ⚠️ `updateUserRoles` - если планируется использовать

---

## 🎯 Приоритет исправлений

**Высокий приоритет:**
- Двойная загрузка пользователя (влияет на производительность)
- Неиспользуемый `corsFilter` bean

**Средний приоритет:**
- Методы-прокси в `AuthService`
- Дублирование `@CrossOrigin`

**Низкий приоритет:**
- Мелкие упрощения в `UserService`
