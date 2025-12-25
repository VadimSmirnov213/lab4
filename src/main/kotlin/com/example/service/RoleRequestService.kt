package com.example.service

import com.example.entity.RequestStatus
import com.example.entity.Role
import com.example.entity.RoleRequest
import com.example.entity.User
import com.example.exception.ValidationException
import com.example.repository.RoleRequestRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class RoleRequestService(
    private val roleRequestRepository: RoleRequestRepository,
    private val userService: UserService
) {
    
    fun createRequest(user: User, requestedRole: Role): RoleRequest {
        // Проверка: пользователь уже имеет эту роль?
        if (user.roles.contains(requestedRole)) {
            throw ValidationException("У вас уже есть роль ${requestedRole.name}")
        }
        
        // Проверка: есть ли уже активный запрос на эту роль?
        val existingRequests = roleRequestRepository.findByUserAndRequestedRoleAndStatus(
            user,
            requestedRole,
            RequestStatus.PENDING
        )
        if (existingRequests.isNotEmpty()) {
            throw ValidationException("У вас уже есть активный запрос на роль ${requestedRole.name}")
        }
        
        val request = RoleRequest(
            user = user,
            requestedRole = requestedRole,
            status = RequestStatus.PENDING,
            createdAt = LocalDateTime.now()
        )
        
        return roleRequestRepository.save(request)
    }
    
    fun getAllPendingRequests(): List<RoleRequest> {
        return roleRequestRepository.findByStatus(RequestStatus.PENDING)
    }
    
    fun getAllRequests(): List<RoleRequest> {
        return roleRequestRepository.findAll()
    }
    
    @Transactional
    fun approveRequest(requestId: Long): RoleRequest {
        val request = roleRequestRepository.findById(requestId)
            .orElseThrow { com.example.exception.UserNotFoundException("Запрос не найден") }
        
        if (request.status != RequestStatus.PENDING) {
            throw ValidationException("Запрос уже обработан")
        }
        
        // Обновляем статус запроса
        val updatedRequest = request.copy(status = RequestStatus.APPROVED)
        roleRequestRepository.save(updatedRequest)
        
        // Назначаем роль пользователю
        val user = request.user
        val updatedRoles = user.roles + request.requestedRole
        userService.updateUserRoles(user.id, updatedRoles)
        
        return updatedRequest
    }
    
    @Transactional
    fun rejectRequest(requestId: Long): RoleRequest {
        val request = roleRequestRepository.findById(requestId)
            .orElseThrow { com.example.exception.UserNotFoundException("Запрос не найден") }
        
        if (request.status != RequestStatus.PENDING) {
            throw ValidationException("Запрос уже обработан")
        }
        
        val updatedRequest = request.copy(status = RequestStatus.REJECTED)
        return roleRequestRepository.save(updatedRequest)
    }
    
    fun getUserRequests(user: User): List<RoleRequest> {
        return roleRequestRepository.findByUser(user)
    }
}
