package com.example.service

import com.example.dto.AuthResponse
import com.example.entity.User
import com.example.exception.UnauthorizedException
import com.example.exception.UserNotFoundException
import com.example.exception.ValidationException
import org.springframework.stereotype.Service

@Service
class AuthService(
    private val userService: UserService,
    private val jwtService: JwtService
) {
    
    fun register(login: String?, password: String?): AuthResponse {
        validateLoginAndPassword(login, password)
        
        val user = userService.createUser(login!!, password!!)
        val token = generateToken(user)
        return AuthResponse(
            success = true,
            message = "Регистрация выполнена успешно",
            token = token
        )
    }
    
    fun login(login: String?, password: String?): AuthResponse {
        validateLoginAndPassword(login, password)
        
        val user = userService.authenticate(login!!, password!!)
        
        return if (user.isPresent) {
            val token = generateToken(user.get())
            AuthResponse(
                success = true,
                message = "Вход выполнен успешно",
                token = token
            )
        } else {
            throw UnauthorizedException("Неверный логин или пароль")
        }
    }
    
    private fun validateLoginAndPassword(login: String?, password: String?) {
        if (login.isNullOrBlank()) {
            throw ValidationException("Логин не может быть пустым")
        }
        if (password.isNullOrBlank()) {
            throw ValidationException("Пароль не может быть пустым")
        }
    }
    
    fun getCurrentUser(token: String): User {
        if (!jwtService.validateToken(token)) {
            throw UnauthorizedException("Недействительный токен")
        }
        
        val userId = jwtService.getUserIdFromToken(token)
        return userService.findById(userId)
            .orElseThrow { UserNotFoundException("Пользователь не найден") }
    }
    
    fun generateToken(user: User): String {
        return jwtService.generateToken(user.id, user.login)
    }
    
    fun validateToken(token: String): Boolean {
        return jwtService.validateToken(token)
    }
    
    fun getUserIdFromToken(token: String): Long {
        return jwtService.getUserIdFromToken(token)
    }
    
    fun getLoginFromToken(token: String): String {
        return jwtService.getLoginFromToken(token)
    }
}
