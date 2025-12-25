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
    fun getAllUsersStatistics(): ResponseEntity<List<com.example.service.UserStatistics>> {
        val statistics = analyticsService.getAllUsersStatistics()
        return ResponseEntity.ok(statistics)
    }
    
    @PreAuthorize("hasRole('ANALYST')")
    @GetMapping("/users/{userId}")
    fun getUserStatistics(@PathVariable userId: Long): ResponseEntity<com.example.service.UserStatistics> {
        val statistics = analyticsService.getUserStatistics(userId)
        return ResponseEntity.ok(statistics)
    }
}
