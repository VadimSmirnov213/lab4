package com.example.repository

import com.example.entity.Role
import com.example.entity.User
import com.example.repository.UserRepository
import jakarta.annotation.PostConstruct
import org.springframework.stereotype.Component

@Component
class DataInitializer(
    private val userRepository: UserRepository
) {
    
    @PostConstruct
    fun init() {
        val adminPasswordHash = "\$2a\$10\$3yBVJx7011txOF/RU4p1FeLs3EkFD29a2OIyNcAjrrIo4br5D2tYS"
        
        if (userRepository.findByLogin("admin").isEmpty) {
            val admin = User(
                login = "admin",
                passwordHash = adminPasswordHash,
                roles = setOf(Role.ADMIN)
            )
            userRepository.save(admin)
        }
    }
}

