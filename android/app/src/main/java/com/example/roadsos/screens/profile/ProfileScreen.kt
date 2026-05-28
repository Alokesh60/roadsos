package com.example.roadsos.screens.profile

import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.tooling.preview.Preview
import com.example.roadsos.theme.RoadSoSTheme
import coil.compose.AsyncImage
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import com.example.roadsos.viewmodel.ProfileState
import com.example.roadsos.viewmodel.ProfileViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onBack: () -> Unit,
    onOpenPermissions: () -> Unit,
    onLogout: () -> Unit
) {
    BackHandler { onBack() }
    val context = LocalContext.current
    val isPreview = androidx.compose.ui.platform.LocalInspectionMode.current
    val viewModel: ProfileViewModel? = if (isPreview) null else viewModel()

    val profileState = viewModel?.profileState?.collectAsState()?.value ?: ProfileState.Idle

    LaunchedEffect(Unit) {
        viewModel?.fetchProfile()
    }

    val userProfile = if (isPreview) {
        com.example.roadsos.viewmodel.UserProfile(
            name = "John Doe",
            phone = "+1234567890",
            profileUrl = ""
        )
    } else if (profileState is ProfileState.Success) {
        profileState.profile
    } else {
        com.example.roadsos.viewmodel.UserProfile()
    }

    var showNameDialog by remember { mutableStateOf(false) }
    var showBottomSheet by remember { mutableStateOf(false) }
    var showLogoutDialog by remember { mutableStateOf(false) }
    var showDeleteDialog by remember { mutableStateOf(false) }

    val photoPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickVisualMedia(),
        onResult = { uri: Uri? ->
            if (uri != null) {
                viewModel?.uploadProfilePicture(uri, context)
            }
        }
    )

    // Name Dialog
    if (showNameDialog) {
        var tempName by remember { mutableStateOf(userProfile.name) }
        AlertDialog(
            onDismissRequest = { showNameDialog = false },
            title = { Text(text = "Enter your name", color = TextWhite) },
            text = {
                OutlinedTextField(
                    value = tempName,
                    onValueChange = { tempName = it },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextWhite,
                        unfocusedTextColor = TextWhite,
                        focusedBorderColor = Color.Gray,
                        unfocusedBorderColor = Color.LightGray
                    )
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    viewModel?.updateName(tempName)
                    showNameDialog = false
                }) {
                    Text("Save", color = PrimaryRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showNameDialog = false }) {
                    Text("Cancel", color = TextGray)
                }
            },
            containerColor = CardBackground
        )
    }

    // Logout Dialog
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text("Logout", color = Color.White) },
            text = { Text("Are you sure you want to log out?", color = TextWhite) },
            confirmButton = {
                TextButton(onClick = {
                    showLogoutDialog = false
                    viewModel?.logout()
                    onLogout()
                }) {
                    Text("Logout", color = PrimaryRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel", color = TextGray)
                }
            },
            containerColor = CardBackground
        )
    }

    // Delete Dialog
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = { Text("Delete Account", color = Color.White) },
            text = {
                Text(
                    "Are you sure you want to delete your account? This action cannot be undone.",
                    color = TextWhite
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    showDeleteDialog = false
                    viewModel?.deleteAccount(
                        onSuccess = { onLogout() },
                        onError = {} // Handle error appropriately
                    )
                }) {
                    Text("Delete", color = PrimaryRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) {
                    Text("Cancel", color = TextGray)
                }
            },
            containerColor = CardBackground
        )
    }

    // Profile Photo Bottom Sheet
    if (showBottomSheet) {
        ModalBottomSheet(
            onDismissRequest = { showBottomSheet = false },
            containerColor = CardBackground
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "Profile picture",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = TextWhite
                    )
                    IconButton(onClick = {
                        viewModel?.deleteProfilePicture()
                        showBottomSheet = false
                    }) {
                        Icon(Icons.Default.Delete, contentDescription = "Delete", tint = TextWhite)
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            // Can't directly open camera without more permissions handling in a simple way
                            // Will open photo picker instead as a fallback for both or just use photo picker.
                            photoPickerLauncher.launch(
                                androidx.activity.result.PickVisualMediaRequest(
                                    ActivityResultContracts.PickVisualMedia.ImageOnly
                                )
                            )
                            showBottomSheet = false
                        }
                        .padding(vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.CameraAlt, contentDescription = "Camera", tint = TextWhite)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Camera", fontSize = 16.sp, color = TextWhite)
                }
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            photoPickerLauncher.launch(
                                androidx.activity.result.PickVisualMediaRequest(
                                    ActivityResultContracts.PickVisualMedia.ImageOnly
                                )
                            )
                            showBottomSheet = false
                        }
                        .padding(vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.PhotoLibrary,
                        contentDescription = "Gallery",
                        tint = TextWhite
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Gallery", fontSize = 16.sp, color = TextWhite)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .systemBarsPadding()
                .imePadding()
                .verticalScroll(rememberScrollState())
        ) {
            // TOP BAR

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(DarkBackground)
                    .padding(
                        horizontal = 16.dp,
                        vertical = 16.dp
                    ),

                verticalAlignment =
                    Alignment.CenterVertically
            ) {

                IconButton(
                    onClick = onBack
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.ArrowBack,
                        contentDescription =
                            "Back",
                        tint =
                            TextWhite
                    )
                }

                Spacer(
                    modifier =
                        Modifier.width(16.dp)
                )

                Text(
                    text = "Profile",

                    color =
                        TextWhite,

                    fontSize =
                        22.sp,

                    fontWeight =
                        FontWeight.SemiBold
                )
            }


            // PROFILE ICON
            Box(
                modifier = Modifier
                    .size(140.dp)
                    .align(Alignment.CenterHorizontally)
            ) {
                if (userProfile.profileUrl.isNotEmpty()) {
                    AsyncImage(
                        model = userProfile.profileUrl,
                        contentDescription = "Profile Picture",
                        contentScale = ContentScale.Crop,
                        modifier = Modifier
                            .size(140.dp)
                            .clip(CircleShape)
                    )
                } else {
                    Box(
                        modifier = Modifier
                            .size(140.dp)
                            .clip(CircleShape)
                            .background(Color.Gray),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(80.dp)
                        )
                    }
                }

                // Yellow Edit FAB
                Box(
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .size(48.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(PrimaryRed)
                        .clickable { showBottomSheet = true },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = "Edit Profile Picture",
                        tint = TextWhite,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(42.dp))

            // NAME CARD
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp),
                colors = CardDefaults.cardColors(containerColor = CardBackground),
                shape = RoundedCornerShape(16.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        tint = TextWhite,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Name", color = TextGray, fontSize = 14.sp)
                        Text(
                            text = userProfile.name.ifEmpty { "Enter your name" },
                            color = TextWhite,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "This is not your username or pin. This name will be visible to your Connect contacts.",
                            color = TextGray,
                            fontSize = 12.sp,
                            lineHeight = 16.sp
                        )
                    }
                    IconButton(onClick = { showNameDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.Edit,
                            contentDescription = "Edit Name",
                            tint = TextWhite
                        )
                    }
                }

                Spacer(modifier = Modifier.height(26.dp))

                // PERMISSION SETTINGS (keeping this for consistency but updating colors slightly)
                Card(
                    onClick = onOpenPermissions,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp),
                    colors = CardDefaults.cardColors(containerColor = CardBackground),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = null,
                            tint = TextWhite
                        )
                        Spacer(modifier = Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Edit Permission Setting",
                                color = TextWhite,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(26.dp))

                // DELETE ACCOUNT
                Card(
                    onClick = { showDeleteDialog = true },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp),
                    colors = CardDefaults.cardColors(containerColor = CardBackground),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = null,
                            tint = PrimaryRed
                        )
                        Spacer(modifier = Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Delete Account",
                                color = PrimaryRed,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(26.dp))

                // LOGOUT
                OutlinedButton(
                    onClick = { showLogoutDialog = true },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp)
                        .height(54.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = PrimaryRed)
                ) {
                    Icon(imageVector = Icons.Default.Logout, contentDescription = null)
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(text = "Logout", fontWeight = FontWeight.Medium)
                }
            }
        }
    }

    @Preview(showBackground = true, showSystemUi = true)
    @Composable
    fun ProfileScreenPreview() {
        RoadSoSTheme {
            ProfileScreen(
                onBack = {},
                onOpenPermissions = {},
                onLogout = {}
            )
        }
    }
}