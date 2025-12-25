package com.example.entity

import jakarta.persistence.*

@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_seq")
    @SequenceGenerator(name = "user_seq", sequenceName = "user_seq", allocationSize = 1)
    val id: Long = 0,
    
    @Column(nullable = false, unique = true)
    val login: String,
    
    @Column(nullable = false)
    val passwordHash: String
)

