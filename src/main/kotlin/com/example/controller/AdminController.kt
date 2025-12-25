package com.example.controller

import com.example.entity.User
import com.example.exception.ValidationException
import com.example.service.UserService
import org.springframework.http.ResponseEntity
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AdminController(
    private val userService: UserService
) {
    
    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/users/{login}")
    fun deleteUserByLogin( 
        @PathVariable login: String,
        authentication: Authentication
    ): ResponseEntity<Map<String, String>> {
        // Защита: админ не может удалить сам себя
        val currentUser = authentication.principal as User
        if (currentUser.login == login) {
            throw ValidationException("Нельзя удалить самого себя")
        }
        
        userService.deleteUserByLogin(login)
        return ResponseEntity.ok(mapOf("message" to "Пользователь удален"))
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @PatchMapping("/users/{login}/analyst")
    fun assignAnalystRole(
        @PathVariable login: String
    ): ResponseEntity<Map<String, Any>> {
        val updatedUser = userService.assignAnalystRoleByLogin(login)
        return ResponseEntity.ok(mapOf(
            "id" to updatedUser.id,
            "login" to updatedUser.login,
            "roles" to updatedUser.roles.map { it.name },
            "message" to "Роль ANALYST назначена пользователю"
        ))
    }
}
