package com.example.service

import com.example.entity.User
import com.example.exception.UserNotFoundException
import com.example.repository.PointRepository
import org.springframework.stereotype.Service

data class UserStatistics(
    val userId: Long,
    val login: String,
    val totalPoints: Long,
    val hitPoints: Long,
    val hitPercentage: Double
)

@Service
class AnalyticsService(
    private val pointRepository: PointRepository,
    private val userService: UserService
) {
    
    fun getAllUsersStatistics(): List<UserStatistics> {
        val users = userService.findAll()
        
        return users.map { user ->
            val allPoints = pointRepository.findByUserOrderByExecutionTimeDesc(user)
            val totalPoints = allPoints.size.toLong()
            val hitPoints = allPoints.count { it.hit }.toLong()
            val hitPercentage = if (totalPoints > 0) {
                (hitPoints.toDouble() / totalPoints.toDouble()) * 100.0
            } else {
                0.0
            }
            
            UserStatistics(
                userId = user.id,
                login = user.login,
                totalPoints = totalPoints,
                hitPoints = hitPoints,
                hitPercentage = hitPercentage
            )
        }
    }
    
    fun getUserStatistics(userId: Long): UserStatistics {
        val user = userService.findById(userId)
            .orElseThrow { UserNotFoundException("Пользователь не найден") }
        
        val allPoints = pointRepository.findByUserOrderByExecutionTimeDesc(user)
        val totalPoints = allPoints.size.toLong()
        val hitPoints = allPoints.count { it.hit }.toLong()
        val hitPercentage = if (totalPoints > 0) {
            (hitPoints.toDouble() / totalPoints.toDouble()) * 100.0
        } else {
            0.0
        }
        
        return UserStatistics(
            userId = user.id,
            login = user.login,
            totalPoints = totalPoints,
            hitPoints = hitPoints,
            hitPercentage = hitPercentage
        )
    }
    
    fun getUserStatisticsByLogin(login: String): UserStatistics {
        val user = userService.findByLogin(login)
            .orElseThrow { UserNotFoundException("Пользователь не найден") }
        
        val allPoints = pointRepository.findByUserOrderByExecutionTimeDesc(user)
        val totalPoints = allPoints.size.toLong()
        val hitPoints = allPoints.count { it.hit }.toLong()
        val hitPercentage = if (totalPoints > 0) {
            (hitPoints.toDouble() / totalPoints.toDouble()) * 100.0
        } else {
            0.0
        }
        
        return UserStatistics(
            userId = user.id,
            login = user.login,
            totalPoints = totalPoints,
            hitPoints = hitPoints,
            hitPercentage = hitPercentage
        )
    }
    
    fun getAllUsers(): List<Map<String, Any>> {
        val users = userService.findAll()
        return users.map { user ->
            mapOf(
                "id" to user.id,
                "login" to user.login,
                "roles" to user.roles.map { it.name }
            )
        }
    }
}
