package com.example.roadsos.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite

@Composable
fun ErrorBanner(
    message: String
) {

    Card(
        modifier = Modifier.fillMaxWidth(),

        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF2A1212)
        ),

        shape = RoundedCornerShape(18.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),

            verticalAlignment = Alignment.CenterVertically
        ) {

            Text(
                text = "⚠",
                fontSize = 20.sp
            )

            Spacer(modifier = Modifier.width(12.dp))

            Text(
                text = message,
                color = Color(0xFFFF8A8A),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
fun NoInternetBanner() {

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFD32F2F))
            .padding(vertical = 10.dp),

        contentAlignment = Alignment.Center
    ) {

        Text(
            text = "No Internet Connection",
            color = Color.White,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
fun LoadingView() {

    Box(
        modifier = Modifier.fillMaxWidth(),

        contentAlignment = Alignment.Center
    ) {

        CircularProgressIndicator(
            color = PrimaryRed
        )
    }
}

@Composable
fun EmptyStateCard(
    title: String,
    subtitle: String
) {

    Card(
        modifier = Modifier.fillMaxWidth(),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(24.dp)
    ) {

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),

            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            Text(
                text = title,
                color = TextWhite,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = subtitle,
                color = TextGray,
                fontSize = 14.sp
            )
        }
    }
}

@Composable
fun RetryButton(
    onRetry: () -> Unit
) {

    Button(
        onClick = onRetry,

        colors = ButtonDefaults.buttonColors(
            containerColor = PrimaryRed
        ),

        shape = RoundedCornerShape(18.dp)
    ) {

        Text(
            text = "Retry"
        )
    }
}