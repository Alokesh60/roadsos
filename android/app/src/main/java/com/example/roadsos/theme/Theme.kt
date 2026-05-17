package com.example.roadsos.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val RoadSoSColorScheme = darkColorScheme(

    primary = PrimaryRed,

    background = DarkBackground,

    surface = CardBackground,

    onPrimary = TextWhite,

    onBackground = TextWhite,

    onSurface = TextWhite
)

@Composable
fun RoadSoSTheme(
    darkTheme: Boolean = true,
    content: @Composable () -> Unit
) {

    MaterialTheme(
        colorScheme = RoadSoSColorScheme,
        typography = Typography,
        content = content
    )
}