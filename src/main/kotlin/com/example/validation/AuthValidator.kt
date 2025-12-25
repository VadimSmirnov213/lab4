package com.example.validation

import com.example.exception.ValidationException

object AuthValidator {
    
    fun validateLoginAndPassword(login: String?, password: String?) {
        val errors = mutableListOf<String>()
        
        if (login.isNullOrBlank()) {
            errors.add("Логин не может быть пустым")
        }
        
        if (password.isNullOrBlank()) {
            errors.add("Пароль не может быть пустым")
        }
        
        if (errors.isNotEmpty()) {
            throw ValidationException(errors.joinToString(", "))
        }
    }
}

