package com.example.dto

data class AuthResponse(
    val success: Boolean,
    val message: String,
    val token: String? = null
)
