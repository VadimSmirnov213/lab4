package com.example.service

import com.example.entity.Role
import com.example.entity.User
import com.example.repository.UserRepository
import com.example.validation.UserValidator
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
        return passwordEncoder.encode(password)!! 
    }
    
    fun findById(id: Long): Optional<User> {
        return userRepository.findById(id)
    }
    
    fun findAll(): List<User> {
        return userRepository.findAll()
    }
    
    fun createUser(login: String, password: String, roles: Set<Role> = setOf(Role.USER)): User {
        val existingUser = userRepository.findByLogin(login)
        UserValidator.validateUserNotExists(existingUser)
        
        val passwordHash = hashPassword(password)
        val user = User(login = login, passwordHash = passwordHash, roles = roles)
        return userRepository.save(user)
    }
    
    fun deleteUser(userId: Long) {
        val exists = userRepository.existsById(userId)
        UserValidator.validateUserExistsById(exists)
        userRepository.deleteById(userId)
    }
    
    fun deleteUserByLogin(login: String) {
        val user = userRepository.findByLogin(login)
        UserValidator.validateUserExists(user)
        userRepository.deleteById(user.get().id)
    }
    
    fun assignAnalystRoleByLogin(login: String): User {
        val user = userRepository.findByLogin(login)
        UserValidator.validateUserExists(user)
        
        val existingUser = user.get()
        val updatedRoles = existingUser.roles.toMutableSet()
        updatedRoles.add(Role.ANALYST)
        
        val updatedUser = existingUser.copy(roles = updatedRoles)
        return userRepository.save(updatedUser)
    }
}

