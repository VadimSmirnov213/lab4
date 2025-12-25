package com.example.controller

import com.example.entity.Role
import com.example.entity.User
import com.example.exception.ValidationException
import com.example.service.RoleRequestService
import com.example.service.UserService
import org.springframework.http.ResponseEntity
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AdminController(
    private val userService: UserService,
    private val roleRequestService: RoleRequestService
) {
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/users")
    fun getAllUsers(): ResponseEntity<List<Map<String, Any>>> {
        val users = userService.findAll()
        val result = users.map { user ->
            mapOf(
                "id" to user.id,
                "login" to user.login,
                "roles" to user.roles.map { it.name }
            )
        }
        return ResponseEntity.ok(result)
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/users/{userId}")
    fun deleteUser(
        @PathVariable userId: Long,
        authentication: Authentication
    ): ResponseEntity<Map<String, String>> {
        // Защита: админ не может удалить сам себя
        val currentUser = authentication.principal as User
        if (currentUser.id == userId) {
            throw ValidationException("Нельзя удалить самого себя")
        }
        
        userService.deleteUser(userId)
        return ResponseEntity.ok(mapOf("message" to "Пользователь удален"))
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @PutMapping("/users/{userId}/roles")
    fun updateUserRoles(
        @PathVariable userId: Long,
        @RequestBody request: Map<String, List<String>>,
        authentication: Authentication
    ): ResponseEntity<Map<String, Any>> {
        // Защита: админ не может изменить свои роли
        val currentUser = authentication.principal as User
        if (currentUser.id == userId) {
            throw ValidationException("Нельзя изменить свои роли")
        }
        
        val roles = request["roles"]?.map { roleName ->
            try {
                Role.valueOf(roleName.uppercase())
            } catch (e: IllegalArgumentException) {
                throw ValidationException("Неизвестная роль: $roleName")
            }
        }?.toSet() 
            ?: throw ValidationException("Роли не указаны")
        
        val updatedUser = userService.updateUserRoles(userId, roles)
        return ResponseEntity.ok(mapOf(
            "id" to updatedUser.id,
            "login" to updatedUser.login,
            "roles" to updatedUser.roles.map { it.name }
        ))
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/requests")
    fun getAllRequests(): ResponseEntity<List<Map<String, Any>>> {
        val requests = roleRequestService.getAllRequests()
        val result = requests.map { request ->
            mapOf(
                "id" to request.id,
                "userId" to request.user.id,
                "userLogin" to request.user.login,
                "requestedRole" to request.requestedRole.name,
                "status" to request.status.name,
                "createdAt" to request.createdAt
            )
        }
        return ResponseEntity.ok(result)
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/requests/pending")
    fun getPendingRequests(): ResponseEntity<List<Map<String, Any>>> {
        val requests = roleRequestService.getAllPendingRequests()
        val result = requests.map { request ->
            mapOf(
                "id" to request.id,
                "userId" to request.user.id,
                "userLogin" to request.user.login,
                "requestedRole" to request.requestedRole.name,
                "status" to request.status.name,
                "createdAt" to request.createdAt
            )
        }
        return ResponseEntity.ok(result)
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @PutMapping("/requests/{requestId}/approve")
    fun approveRequest(@PathVariable requestId: Long): ResponseEntity<Map<String, Any>> {
        val request = roleRequestService.approveRequest(requestId)
        return ResponseEntity.ok(mapOf(
            "id" to request.id,
            "message" to "Запрос одобрен, роль ${request.requestedRole.name} назначена пользователю",
            "status" to request.status.name
        ))
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @PutMapping("/requests/{requestId}/reject")
    fun rejectRequest(@PathVariable requestId: Long): ResponseEntity<Map<String, Any>> {
        val request = roleRequestService.rejectRequest(requestId)
        return ResponseEntity.ok(mapOf(
            "id" to request.id,
            "message" to "Запрос отклонен",
            "status" to request.status.name
        ))
    }
}
