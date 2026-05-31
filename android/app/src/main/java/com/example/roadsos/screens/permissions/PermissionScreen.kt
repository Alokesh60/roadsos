package com.example.roadsos.screens.permissions

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Sms
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import androidx.activity.compose.BackHandler
import androidx.compose.ui.tooling.preview.Preview
import com.example.roadsos.theme.RoadSoSTheme

@Composable
fun PermissionScreen(
    onBack: () -> Unit,
    onContinue: () -> Unit
) {
    BackHandler {

        onBack()
    }

    val context = LocalContext.current

    var locationChecked by remember { mutableStateOf(false) }
    var callChecked by remember { mutableStateOf(false) }
    var smsChecked by remember { mutableStateOf(false) }
    var notificationChecked by remember { mutableStateOf(false) }

    val lifecycleOwner = androidx.lifecycle.compose.LocalLifecycleOwner.current

    DisposableEffect(lifecycleOwner) {
        val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
            if (event == androidx.lifecycle.Lifecycle.Event.ON_RESUME) {
                locationChecked = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                callChecked = ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED
                smsChecked = ContextCompat.checkSelfPermission(context, Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED
                notificationChecked = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
                } else {
                    true
                }
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    val openSettings = {
        val intent = android.content.Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = android.net.Uri.fromParts("package", context.packageName, null)
        }
        context.startActivity(intent)
        Toast.makeText(context, "Please revoke the permission here", Toast.LENGTH_LONG).show()
    }

    val locationLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        locationChecked = isGranted
    }
    val callLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        callChecked = isGranted
    }
    val smsLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        smsChecked = isGranted
    }
    val notificationLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        notificationChecked = isGranted
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(horizontal = 20.dp)
    ) {

        Spacer(modifier = Modifier.height(46.dp))

        // TOP BAR

        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {

            IconButton(
                onClick = onBack
            ) {

                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = null,
                    tint = TextWhite
                )
            }

            Spacer(modifier = Modifier.width(6.dp))

            Text(
                text = "Permissions",
                color = TextWhite,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "Manage Permissions",
            color = TextWhite,
            fontSize = 30.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(14.dp))

        Text(
            text = "RoadSoS needs these permissions to provide emergency services quickly and safely.",
            color = TextGray,
            fontSize = 15.sp,
            lineHeight = 24.sp
        )

        Spacer(modifier = Modifier.height(32.dp))

        PermissionCard(
            title = "Location Access",
            description = "Find nearby hospitals and emergency services",
            icon = {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = PrimaryRed,
                    modifier = Modifier.size(28.dp)
                )
            },
            checked = locationChecked,
            onCheckedChange = { isChecked ->
                if (isChecked) {
                    locationLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                } else {
                    openSettings()
                }
            }
        )

        Spacer(modifier = Modifier.height(14.dp))

        PermissionCard(
            title = "Phone Calls",
            description = "Call ambulance and emergency contacts instantly",
            icon = {
                Icon(
                    imageVector = Icons.Default.Call,
                    contentDescription = null,
                    tint = PrimaryRed,
                    modifier = Modifier.size(26.dp)
                )
            },
            checked = callChecked,
            onCheckedChange = { isChecked ->
                if (isChecked) {
                    callLauncher.launch(Manifest.permission.CALL_PHONE)
                } else {
                    openSettings()
                }
            }
        )

        Spacer(modifier = Modifier.height(14.dp))

        PermissionCard(
            title = "SMS Access",
            description = "Share live location during emergencies",
            icon = {
                Icon(
                    imageVector = Icons.Default.Sms,
                    contentDescription = null,
                    tint = PrimaryRed,
                    modifier = Modifier.size(26.dp)
                )
            },
            checked = smsChecked,
            onCheckedChange = { isChecked ->
                if (isChecked) {
                    smsLauncher.launch(Manifest.permission.SEND_SMS)
                } else {
                    openSettings()
                }
            }
        )

        Spacer(modifier = Modifier.height(14.dp))

        PermissionCard(
            title = "Notifications",
            description = "Receive important alerts and updates",
            icon = {
                Icon(
                    imageVector = Icons.Default.Notifications,
                    contentDescription = null,
                    tint = PrimaryRed,
                    modifier = Modifier.size(26.dp)
                )
            },
            checked = notificationChecked,
            onCheckedChange = { isChecked ->
                if (isChecked) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        notificationLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                    } else {
                        notificationChecked = true
                    }
                } else {
                    openSettings()
                }
            }
        )

        Spacer(modifier = Modifier.height(36.dp))

        Button(
            onClick = onContinue,

            modifier = Modifier
                .fillMaxWidth()
                .height(58.dp),

            shape = RoundedCornerShape(22.dp),

            colors = ButtonDefaults.buttonColors(
                containerColor = PrimaryRed
            )
        ) {

            Text(
                text = "Save and Continue",
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(22.dp))

        Text(
            text = "We never share your data.",
            color = TextGray,
            fontSize = 13.sp,

            modifier = Modifier.align(
                Alignment.CenterHorizontally
            )
        )
    }
}

@Composable
fun PermissionCard(
    title: String,
    description: String,
    icon: @Composable () -> Unit,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {

    Card(
        modifier = Modifier.fillMaxWidth(),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(22.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),

            verticalAlignment = Alignment.CenterVertically
        ) {

            Box(
                modifier = Modifier
                    .size(58.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF151922)),

                contentAlignment = Alignment.Center
            ) {
                icon()
            }

            Spacer(modifier = Modifier.width(14.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {

                Text(
                    text = title,
                    color = TextWhite,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = description,
                    color = TextGray,
                    fontSize = 13.sp,
                    lineHeight = 20.sp
                )
            }

            Checkbox(
                checked = checked,
                onCheckedChange = onCheckedChange,

                colors = CheckboxDefaults.colors(
                    checkedColor = PrimaryRed,
                    uncheckedColor = PrimaryRed,
                    checkmarkColor = Color.White
                )
            )
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun PermissionScreenPreview() {
    RoadSoSTheme {
        PermissionScreen(onBack = {}, onContinue = {})
    }
}