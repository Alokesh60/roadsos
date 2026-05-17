package com.example.roadsos.screens.splash

import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.R
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite

@Composable
fun SplashScreen() {

    val infiniteTransition =
        rememberInfiniteTransition(label = "")

    val scale by infiniteTransition.animateFloat(
        initialValue = 0.92f,
        targetValue = 1.05f,

        animationSpec = infiniteRepeatable(
            animation = tween(1400),
            repeatMode = RepeatMode.Reverse
        ),

        label = ""
    )

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        // BACKGROUND IMAGE

        Image(
            painter = painterResource(
                id = R.drawable.splash_bg
            ),

            contentDescription = null,

            modifier = Modifier.fillMaxSize(),

            contentScale = ContentScale.Crop
        )

        // DARK OVERLAY

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Color.Black.copy(alpha = 0.55f)
                )
        )

        // RED GLOW

        Box(
            modifier = Modifier
                .size(260.dp)
                .align(Alignment.Center)
                .blur(60.dp)
                .background(
                    Brush.radialGradient(
                        colors = listOf(
                            PrimaryRed.copy(alpha = 0.35f),
                            Color.Transparent
                        )
                    )
                )
        )

        // CONTENT

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(bottom = 70.dp),

            horizontalAlignment =
                Alignment.CenterHorizontally,

            verticalArrangement =
                Arrangement.Center
        ) {

            // SOS ICON

            Box(
                modifier = Modifier
                    .scale(scale)
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = listOf(
                                Color(0xFFFF6666),
                                PrimaryRed
                            )
                        )
                    ),

                contentAlignment = Alignment.Center
            ) {

                Text(
                    text = "SOS",
                    color = TextWhite,
                    fontSize = 34.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }

            Spacer(modifier = Modifier.height(30.dp))

            // APP NAME

            Row {

                Text(
                    text = "Road",
                    color = TextWhite,
                    fontSize = 40.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Text(
                    text = "SOS",
                    color = PrimaryRed,
                    fontSize = 40.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "Your Safety. Our Priority.",

                color = TextGray,
                fontSize = 15.sp
            )

            Spacer(modifier = Modifier.height(260.dp))

            // LOADING TEXT

            Text(
                text = "Loading...",

                color = TextWhite.copy(alpha = 0.9f),
                fontSize = 14.sp
            )

            Spacer(modifier = Modifier.height(14.dp))

            // PROGRESS BAR

            LinearProgressIndicator(
                modifier = Modifier
                    .width(190.dp)
                    .height(5.dp)
                    .clip(RoundedCornerShape(50.dp)),

                color = PrimaryRed,

                trackColor =
                    Color.White.copy(alpha = 0.15f)
            )
        }
    }
}