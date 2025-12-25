package com.example.repository

import com.example.entity.User
import com.example.repository.UserRepository
import jakarta.annotation.PostConstruct
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Component

@Component
class DataInitializer(
    private val userRepository: UserRepository,
    private val passwordEncoder: PasswordEncoder
) {

    @PostConstruct
    fun init() {
        if (userRepository.findByLogin("user").isEmpty) {
            val passwordHash = requireNotNull(passwordEncoder.encode("123")) { "Password encoding failed" }
            val user = User(
                login = "user",
                passwordHash = passwordHash
            )
            userRepository.save(user)
            println("Создан пользователь: login=user, password=123")
        }
    }
}

