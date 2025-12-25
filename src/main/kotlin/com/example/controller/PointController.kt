package com.example.controller

import com.example.dto.PointDto
import com.example.service.PointService
import jakarta.servlet.http.HttpSession
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api")
@CrossOrigin(originPatterns = ["*"], allowCredentials = "true")
class PointController(
    private val pointService: PointService
) {

    @PostMapping("/check")
    fun checkPoint(
        @RequestBody dto: PointDto,
        session: HttpSession
    ): ResponseEntity<PointDto> {
        val result = pointService.checkAndSavePoint(dto, session)
        return ResponseEntity.ok(result)
    }
    
    @GetMapping("/points")
    fun getPoints(session: HttpSession): ResponseEntity<List<PointDto>> {
        val points = pointService.getPointsByUser(session)
        return ResponseEntity.ok(points)
    }

    @DeleteMapping("/points")
    fun deletePoints(session: HttpSession): ResponseEntity<Map<String, String>> {
        pointService.deletePointsByUser(session)
        return ResponseEntity.ok(mapOf("message" to "Точки удалены"))
    }

    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> {
        return ResponseEntity.ok(mapOf("status" to "ok"))
    }
}
