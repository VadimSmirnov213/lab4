package com.example.service

import com.example.entity.Role
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
    
    fun findAll(): List<User> {
        return userRepository.findAll()
    }
    
    fun createUser(login: String, password: String, roles: Set<Role> = setOf(Role.USER)): User {
        if (userRepository.findByLogin(login).isPresent) {
            throw com.example.exception.UserAlreadyExistsException("Пользователь с таким логином уже существует")
        }
        
        val passwordHash = hashPassword(password)
        val user = User(login = login, passwordHash = passwordHash, roles = roles)
        return userRepository.save(user)
    }
    
    fun deleteUser(userId: Long) {
        if (!userRepository.existsById(userId)) {
            throw com.example.exception.UserNotFoundException("Пользователь не найден")
        }
        userRepository.deleteById(userId)
    }
    
    fun deleteUserByLogin(login: String) {
        val user = userRepository.findByLogin(login)
            .orElseThrow { com.example.exception.UserNotFoundException("Пользователь не найден") }
        userRepository.deleteById(user.id)
    }
    
    fun updateUserRoles(userId: Long, roles: Set<Role>): User {
        val user = userRepository.findById(userId)
            .orElseThrow { com.example.exception.UserNotFoundException("Пользователь не найден") }
        
        val updatedUser = user.copy(roles = roles)
        return userRepository.save(updatedUser)
    }
    
    fun assignAnalystRoleByLogin(login: String): User {
        val user = userRepository.findByLogin(login)
            .orElseThrow { com.example.exception.UserNotFoundException("Пользователь не найден") }
        
        val updatedRoles = user.roles.toMutableSet()
        updatedRoles.add(Role.ANALYST)
        
        val updatedUser = user.copy(roles = updatedRoles)
        return userRepository.save(updatedUser)
    }
}

