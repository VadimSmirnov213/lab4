package com.example.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "points")
data class Point(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "point_seq")
    @SequenceGenerator(name = "point_seq", sequenceName = "point_seq", allocationSize = 1)
    val id: Long = 0,
    
    @Column(nullable = false)
    val x: Double,
    
    @Column(nullable = false)
    val y: Double,
    
    @Column(nullable = false)
    val r: Double,
    
    @Column(nullable = false)
    val hit: Boolean,
    
    @Column(nullable = false)
    val executionTime: LocalDateTime,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User
)

