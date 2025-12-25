package com.example.controller

import com.example.entity.Role
import com.example.entity.User
import com.example.service.RoleRequestService
import org.springframework.http.ResponseEntity
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/requests")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class RoleRequestController(
    private val roleRequestService: RoleRequestService
) {
    
    @PreAuthorize("hasRole('USER')")
    @GetMapping("/my")
    fun getMyRequests(authentication: Authentication): ResponseEntity<List<Map<String, Any>>> {
        val user = authentication.principal as User
        
        val requests = roleRequestService.getUserRequests(user)
        val result = requests.map { request ->
            mapOf(
                "id" to request.id,
                "requestedRole" to request.requestedRole.name,
                "status" to request.status.name,
                "createdAt" to request.createdAt
            )
        }
        
        return ResponseEntity.ok(result)
    }
}
