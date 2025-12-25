package com.example.dto

import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

data class RegisterRequest(
    @field:NotBlank(message = "Логин не может быть пустым")
    @field:Size(min = 3, max = 50, message = "Логин должен быть от 3 до 50 символов")
    val login: String?,
    
    @field:NotBlank(message = "Пароль не может быть пустым")
    @field:Size(min = 3, max = 100, message = "Пароль должен быть от 3 до 100 символов")
    val password: String?
)
