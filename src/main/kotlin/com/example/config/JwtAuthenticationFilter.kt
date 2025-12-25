package com.example.config

import com.example.service.AuthService
import com.example.service.CustomUserDetailsService
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

@Component
class JwtAuthenticationFilter(
    private val authService: AuthService,
    private val userDetailsService: CustomUserDetailsService
) : OncePerRequestFilter() {
    
    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        val authHeader = request.getHeader("Authorization")
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            val token = authHeader.substring(7)
            
            try {
                if (authService.validateToken(token)) {
                    val login = authService.getLoginFromToken(token)
                    // Загружаем User с актуальными ролями из БД
                    val user = authService.getCurrentUser(token)
                    // Загружаем UserDetails для получения authorities
                    val userDetails = userDetailsService.loadUserByUsername(login)
                    
                    val authentication = UsernamePasswordAuthenticationToken(
                        user,  // Передаем User в principal для совместимости
                        null,
                        userDetails.authorities  // Роли для RBAC
                    )
                    authentication.details = WebAuthenticationDetailsSource().buildDetails(request)
                    SecurityContextHolder.getContext().authentication = authentication
                }
            } catch (e: Exception) {
                // Токен невалиден, продолжаем без аутентификации
                SecurityContextHolder.clearContext()
            }
        }
        
        filterChain.doFilter(request, response)
    }
}
