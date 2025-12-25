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
        // Обычный пользователь
        if (userRepository.findByLogin("user").isEmpty) {
            val passwordHash = requireNotNull(passwordEncoder.encode("123")) { "Password encoding failed" }
            val user = User(
                login = "user",
                passwordHash = passwordHash,
                roles = setOf(Role.USER)
            )
            userRepository.save(user)
            println("Создан пользователь: login=user, password=123, role=USER")
        } else {
            // Обновляем существующего пользователя, если у него нет ролей
            val existingUser = userRepository.findByLogin("user").get()
            if (existingUser.roles.isEmpty()) {
                val updatedUser = existingUser.copy(roles = setOf(Role.USER))
                userRepository.save(updatedUser)
                println("Обновлен пользователь: login=user, добавлена роль USER")
            }
        }
        
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
        
        // Аналитик
        if (userRepository.findByLogin("analyst").isEmpty) {
            val passwordHash = requireNotNull(passwordEncoder.encode("analyst")) { "Password encoding failed" }
            val analyst = User(
                login = "analyst",
                passwordHash = passwordHash,
                roles = setOf(Role.ANALYST)
            )
            userRepository.save(analyst)
            println("Создан аналитик: login=analyst, password=analyst, role=ANALYST")
        } else {
            // Обновляем существующего аналитика, если у него нет ролей
            val existingAnalyst = userRepository.findByLogin("analyst").get()
            if (existingAnalyst.roles.isEmpty()) {
                val updatedAnalyst = existingAnalyst.copy(roles = setOf(Role.ANALYST))
                userRepository.save(updatedAnalyst)
                println("Обновлен аналитик: login=analyst, добавлена роль ANALYST")
            }
        }
        
        // Обновляем всех остальных пользователей без ролей - добавляем роль USER
        val allUsers = userRepository.findAll()
        allUsers.forEach { user ->
            if (user.roles.isEmpty() && user.login !in listOf("admin", "analyst")) {
                val updatedUser = user.copy(roles = setOf(Role.USER))
                userRepository.save(updatedUser)
                println("Обновлен пользователь: login=${user.login}, добавлена роль USER")
            }
        }
    }
}

