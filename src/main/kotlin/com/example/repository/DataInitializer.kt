package com.example.repository

import com.example.entity.Role
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
        // Администратор
        if (userRepository.findByLogin("admin").isEmpty) {
            val passwordHash = requireNotNull(passwordEncoder.encode("admin")) { "Password encoding failed" }
            val admin = User(
                login = "admin",
                passwordHash = passwordHash,
                roles = setOf(Role.ADMIN)
            )
            userRepository.save(admin)
            println("Создан администратор: login=admin, password=admin, role=ADMIN")
        } else {
            // Обновляем существующего админа, если у него нет ролей
            val existingAdmin = userRepository.findByLogin("admin").get()
            if (existingAdmin.roles.isEmpty()) {
                val updatedAdmin = existingAdmin.copy(roles = setOf(Role.ADMIN))
                userRepository.save(updatedAdmin)
                println("Обновлен администратор: login=admin, добавлена роль ADMIN")
            }
        }
        
        // Обновляем всех остальных пользователей без ролей - добавляем роль USER
        val allUsers = userRepository.findAll()
        allUsers.forEach { user ->
            if (user.roles.isEmpty() && user.login != "admin") {
                val updatedUser = user.copy(roles = setOf(Role.USER))
                userRepository.save(updatedUser)
                println("Обновлен пользователь: login=${user.login}, добавлена роль USER")
            }
        }
    }
}

