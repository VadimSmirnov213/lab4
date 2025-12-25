package com.example.validation

import com.example.dto.PointDto
import com.example.exception.ValidationException

object PointValidator {
    
    fun validate(dto: PointDto) {
        val errors = mutableListOf<String>()
        
        if (dto.x == null) {
            errors.add("X не может быть null")
        } else {
            if (dto.x < -5.0 || dto.x > 5.0) {
                errors.add("X должно быть от -5 до 5")
            }
        }
        
        if (dto.y == null) {
            errors.add("Y не может быть null")
        } else {
            if (dto.y < -5.0 || dto.y > 3.0) {
                errors.add("Y должно быть от -5 до 3")
            }
        }
        
        if (dto.r == null) {
            errors.add("R не может быть null")
        } else {
            if (dto.r < -5.0 || dto.r > 5.0) {
                errors.add("R должно быть от -5 до 5")
            }
        }
        
        if (errors.isNotEmpty()) {
            throw ValidationException(errors.joinToString(", "))
        }
    }
}

