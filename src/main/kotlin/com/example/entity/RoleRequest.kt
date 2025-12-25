package com.example.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "role_requests")
data class RoleRequest(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "role_request_seq")
    @SequenceGenerator(name = "role_request_seq", sequenceName = "role_request_seq", allocationSize = 1)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User,
    
    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    val requestedRole: Role,
    
    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    val status: RequestStatus = RequestStatus.PENDING,
    
    @Column(nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class RequestStatus {
    PENDING,    // Ожидает рассмотрения
    APPROVED,   // Одобрен
    REJECTED    // Отклонен
}
