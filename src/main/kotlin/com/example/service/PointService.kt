package com.example.service

import com.example.dto.PointDto
import com.example.mapper.PointMapper
import com.example.repository.PointRepository
import com.example.validation.PointValidator
import jakarta.servlet.http.HttpSession
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class PointService(
    private val pointRepository: PointRepository,
    private val authService: AuthService
) {

    fun checkPointInArea(x: Double, y: Double, r: Double): Boolean {
        if (x >= -r && x <= 0 && y >= -r && y <= 0) {
            return true
        }
        
        if (x <= 0 && x >= -r/2 && y >= 0 && y <= r && y <= -2*x + r) {
            return true
        }
        
        if (x >= 0 && x <= r/2 && y >= 0 && y <= r/2 && x*x + y*y <= (r/2)*(r/2)) {
            return true
        }
        
        return false
    }
    
    private fun calculateHit(dto: PointDto): Boolean {
        val x = dto.x!!
        val y = dto.y!!
        val r = dto.r!!
        return checkPointInArea(x, y, r)
    }
    

    @Transactional
    fun checkAndSavePoint(dto: PointDto, session: HttpSession): PointDto {
        PointValidator.validate(dto)
        val user = authService.getCurrentUser(session)
        val hit = calculateHit(dto)
        val executionTime = LocalDateTime.now()
        val point = PointMapper.toEntity(dto, user, hit, executionTime)
        val savedPoint = pointRepository.save(point)
        
        return PointMapper.toDto(savedPoint)
    }
    

    fun getPointsByUser(session: HttpSession): List<PointDto> {
        val user = authService.getCurrentUser(session)
        val points = pointRepository.findByUserOrderByExecutionTimeDesc(user)
        return PointMapper.toDtoList(points)
    }
    

    @Transactional
    fun deletePointsByUser(session: HttpSession) {
        val user = authService.getCurrentUser(session)
        pointRepository.deleteByUser(user)
    }
}
