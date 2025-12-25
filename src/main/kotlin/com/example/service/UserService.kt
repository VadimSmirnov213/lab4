package com.example.service

import com.example.entity.User
import com.example.repository.UserRepository
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import java.util.*

@Service
class UserService(
    private val userRepository: UserRepository,
    private val passwordEncoder: PasswordEncoder
) {
    
    fun authenticate(login: String, password: String): Optional<User> {
        val user = userRepository.findByLogin(login)
        return if (user.isPresent && passwordEncoder.matches(password, user.get().passwordHash)) {
            user
        } else {
            Optional.empty()
        }
    }
    
    fun findByLogin(login: String): Optional<User> {
        return userRepository.findByLogin(login)
    }
    
    fun hashPassword(password: String): String {
        return requireNotNull(passwordEncoder.encode(password)) { "Password encoding failed" }
    }
    
    fun findById(id: Long): Optional<User> {
        return userRepository.findById(id)
    }
}

