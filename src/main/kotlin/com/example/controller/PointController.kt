package com.example.controller

import com.example.dto.PointDto
import com.example.service.PointService
import org.springframework.http.ResponseEntity
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class PointController(
    private val pointService: PointService
) {

    @PreAuthorize("hasAnyRole('USER', 'ADMIN', 'ANALYST')")
    @PostMapping("/check")
    fun checkPoint(
        @RequestBody dto: PointDto,
        authentication: Authentication
    ): ResponseEntity<PointDto> {
        val result = pointService.checkAndSavePoint(dto, authentication)
        return ResponseEntity.ok(result)
    }
    
    @PreAuthorize("hasAnyRole('USER', 'ADMIN', 'ANALYST')")
    @GetMapping("/points")
    fun getPoints(authentication: Authentication): ResponseEntity<List<PointDto>> {
        val points = pointService.getPointsByUser(authentication)
        return ResponseEntity.ok(points)
    }

    @PreAuthorize("hasAnyRole('USER', 'ADMIN', 'ANALYST')")
    @DeleteMapping("/points")
    fun deletePoints(authentication: Authentication): ResponseEntity<Map<String, String>> {
        pointService.deletePointsByUser(authentication)
        return ResponseEntity.ok(mapOf("message" to "Точки удалены"))
    }

    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> {
        return ResponseEntity.ok(mapOf("status" to "ok"))
    }
}
