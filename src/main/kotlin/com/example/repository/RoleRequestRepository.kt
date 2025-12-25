package com.example.repository

import com.example.entity.RequestStatus
import com.example.entity.RoleRequest
import com.example.entity.User
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface RoleRequestRepository : JpaRepository<RoleRequest, Long> {
    fun findByUser(user: User): List<RoleRequest>
    fun findByStatus(status: RequestStatus): List<RoleRequest>
    fun findByUserAndRequestedRoleAndStatus(
        user: User,
        requestedRole: com.example.entity.Role,
        status: RequestStatus
    ): List<RoleRequest>
}
