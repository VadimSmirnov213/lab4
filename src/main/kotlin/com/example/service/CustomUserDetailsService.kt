package com.example.service

import com.example.entity.Role
import com.example.entity.User
import com.example.validation.UserValidator
import org.springframework.security.core.GrantedAuthority
import org.springframework.security.core.authority.SimpleGrantedAuthority
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.stereotype.Service

@Service
class CustomUserDetailsService(
    private val userService: UserService
) : UserDetailsService {
    
    override fun loadUserByUsername(login: String): UserDetails {
        val userOptional = userService.findByLogin(login)
        UserValidator.validateUserExists(userOptional)
        val user = userOptional.get()
        
        return org.springframework.security.core.userdetails.User(
            user.login,
            user.passwordHash,
            getAuthorities(user.roles)
        )
    }
    
    private fun getAuthorities(roles: Set<Role>): Collection<GrantedAuthority> {
        return roles.map { SimpleGrantedAuthority("ROLE_${it.name}") }
    }
}
