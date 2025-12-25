package com.example.dto

import java.time.LocalDateTime

data class PointDto(
    val x: Double?,
    val y: Double?,
    val r: Double?,
    val hit: Boolean? = null,
    val time: LocalDateTime? = null
)

