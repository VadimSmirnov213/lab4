package com.example.controller

import com.example.dto.LoginRequest
import com.example.dto.RegisterRequest
import com.example.service.AuthService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AuthController(
    private val authService: AuthService
) {

    @PostMapping("/register")
    fun register(
        @RequestBody request: RegisterRequest
    ): ResponseEntity<com.example.dto.AuthResponse> {
        return ResponseEntity.ok(
            authService.register(request.login, request.password)
        )
    }

    @PostMapping("/login")
    fun login(
        @RequestBody request: LoginRequest
    ): ResponseEntity<com.example.dto.AuthResponse> {
        return ResponseEntity.ok(
            authService.login(request.login, request.password)
        )
    }
}

