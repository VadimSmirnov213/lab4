package com.example.service

import com.example.dto.PointDto
import com.example.entity.User
import com.example.mapper.PointMapper
import com.example.repository.PointRepository
import com.example.validation.PointValidator
import org.springframework.security.core.Authentication
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class PointService(
    private val pointRepository: PointRepository
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
    
    private fun getCurrentUser(authentication: Authentication): User {
        return authentication.principal as User
    }

    @Transactional
    fun checkAndSavePoint(dto: PointDto, authentication: Authentication): PointDto {
        PointValidator.validate(dto)
        val user = getCurrentUser(authentication)
        val hit = calculateHit(dto)
        val executionTime = LocalDateTime.now()
        val point = PointMapper.toEntity(dto, user, hit, executionTime)
        val savedPoint = pointRepository.save(point)
        
        return PointMapper.toDto(savedPoint)
    }
    

    fun getPointsByUser(authentication: Authentication): List<PointDto> {
        val user = getCurrentUser(authentication)
        val points = pointRepository.findByUserOrderByExecutionTimeDesc(user)
        return PointMapper.toDtoList(points)
    }
    

    @Transactional
    fun deletePointsByUser(authentication: Authentication) {
        val user = getCurrentUser(authentication)
        pointRepository.deleteByUser(user)
    }
}
