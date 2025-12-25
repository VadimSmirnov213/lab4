package com.example.controller

import com.example.dto.LoginRequest
import com.example.service.AuthService
import com.example.service.UserService
import jakarta.servlet.http.HttpSession
import jakarta.validation.Valid
import org.springframework.http.ResponseEntity
import org.springframework.validation.BindingResult
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AuthController(
    private val userService: UserService,
    private val authService: AuthService
) {

    @PostMapping("/login")
    fun login(
        @Valid @RequestBody request: LoginRequest,
        bindingResult: BindingResult,
        session: HttpSession
    ): ResponseEntity<Any> {
        if (bindingResult.hasErrors()) {
            val errors = bindingResult.fieldErrors.associate { it.field to it.defaultMessage }
            return ResponseEntity.badRequest().body(mapOf("errors" to errors))
        }

        val login = request.login!!
        val password = request.password!!
        
        val user = userService.authenticate(login, password)
        
        if (user.isPresent) {
            authService.setUserSession(session, user.get())
            return ResponseEntity.ok(mapOf(
                "success" to true,
                "message" to "Вход выполнен успешно"
            ))
        } else {
            return ResponseEntity.status(401).body(mapOf(
                "success" to false,
                "message" to "Неверный логин или пароль"
            ))
        }
    }
    
    @PostMapping("/logout")
    fun logout(session: HttpSession): ResponseEntity<Map<String, String>> {
        authService.clearSession(session)
        return ResponseEntity.ok(mapOf("message" to "Выход выполнен успешно"))
    }
    
    @GetMapping("/check")
    fun checkAuth(session: HttpSession): ResponseEntity<Any> {
        val isAuthenticated = authService.isAuthenticated(session)
        return if (isAuthenticated) {
            ResponseEntity.ok(mapOf(
                "authenticated" to true,
                "login" to session.getAttribute("userLogin")
            ))
        } else {
            ResponseEntity.status(401).body(mapOf("authenticated" to false))
        }
    }
}

