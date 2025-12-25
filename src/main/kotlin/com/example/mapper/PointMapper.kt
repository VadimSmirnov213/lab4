package com.example.mapper

import com.example.dto.PointDto
import com.example.entity.Point
import com.example.entity.User
import java.time.LocalDateTime

object PointMapper {
    
    fun toEntity(dto: PointDto, user: User, hit: Boolean, executionTime: LocalDateTime): Point {
        return Point(
            x = dto.x!!,
            y = dto.y!!,
            r = dto.r!!,
            hit = hit,
            executionTime = executionTime,
            user = user
        )
    }
    
    fun toDto(point: Point): PointDto {
        return PointDto(
            x = point.x,
            y = point.y,
            r = point.r,
            hit = point.hit,
            time = point.executionTime
        )
    }
    
    fun toDtoList(points: List<Point>): List<PointDto> {
        return points.map { toDto(it) }
    }
}
