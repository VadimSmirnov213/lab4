package com.example.service

import com.example.entity.User
import com.example.exception.UnauthorizedException
import com.example.exception.UserNotFoundException
import jakarta.servlet.http.HttpSession
import org.springframework.stereotype.Service

@Service
class AuthService(
    private val userService: UserService
) {
    
    fun getCurrentUser(session: HttpSession): User {
        val userId = session.getAttribute("userId") as? Long
            ?: throw UnauthorizedException("Требуется авторизация")
        
        return userService.findById(userId)
            .orElseThrow { UserNotFoundException("Пользователь не найден") }
    }
    
    fun setUserSession(session: HttpSession, user: User) {
        session.setAttribute("userId", user.id)
        session.setAttribute("userLogin", user.login)
    }
    
    fun clearSession(session: HttpSession) {
        session.invalidate()
    }
    
    fun isAuthenticated(session: HttpSession): Boolean {
        return session.getAttribute("userId") != null
    }
}
