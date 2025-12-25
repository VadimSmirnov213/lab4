package com.example.repository

import com.example.entity.Point
import com.example.entity.User
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface PointRepository : JpaRepository<Point, Long> {
    fun findByUserOrderByExecutionTimeDesc(user: User): List<Point>
    fun deleteByUser(user: User)
}

