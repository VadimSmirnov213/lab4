package com.example.controller

import com.example.service.AnalyticsService
import org.springframework.http.ResponseEntity
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/analytics")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class AnalyticsController(
    private val analyticsService: AnalyticsService
) {
    
    @PreAuthorize("hasRole('ANALYST')")
    @GetMapping("/users")
    fun getAllUsers(): ResponseEntity<List<Map<String, Any>>> {
        val users = analyticsService.getAllUsers()
        return ResponseEntity.ok(users)
    }
    
    @PreAuthorize("hasRole('ANALYST')")
    @GetMapping("/users/{login}/statistics")
    fun getUserStatisticsByLogin(@PathVariable login: String): ResponseEntity<com.example.service.UserStatistics> {
        val statistics = analyticsService.getUserStatisticsByLogin(login)
        return ResponseEntity.ok(statistics)
    }
}
