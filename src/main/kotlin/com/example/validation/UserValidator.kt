package com.example.validation

import com.example.exception.UserAlreadyExistsException
import com.example.exception.UserNotFoundException
import java.util.*

object UserValidator {
    
    fun validateUserExists(user: Optional<*>, errorMessage: String = "Пользователь не найден") {
        if (user.isEmpty) {
            throw UserNotFoundException(errorMessage)
        }
    }
    
    fun validateUserNotExists(user: Optional<*>, errorMessage: String = "Пользователь с таким логином уже существует") {
        if (user.isPresent) {
            throw UserAlreadyExistsException(errorMessage)
        }
    }
    
    fun validateUserExistsById(exists: Boolean, errorMessage: String = "Пользователь не найден") {
        if (!exists) {
            throw UserNotFoundException(errorMessage)
        }
    }
}

