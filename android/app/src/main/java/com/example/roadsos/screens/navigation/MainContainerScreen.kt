package com.example.roadsos.screens.navigation

import android.widget.Toast
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.example.roadsos.screens.ai.AIAssistantScreen
import com.example.roadsos.screens.contacts.AddContactScreen
import com.example.roadsos.screens.contacts.ContactsScreen
import com.example.roadsos.screens.contacts.EmergencyContact
import com.example.roadsos.screens.home.HomeScreen
import com.example.roadsos.screens.home.HomeScreen
import com.example.roadsos.models.EmergencyService
import com.example.roadsos.models.PlaceCategory
import com.example.roadsos.screens.services.ServiceDetailScreen
import com.example.roadsos.screens.services.ServicesScreen
import com.example.roadsos.screens.profile.ProfileScreen
import com.example.roadsos.screens.permissions.PermissionScreen
import com.example.roadsos.viewmodel.ContactsViewModel
import androidx.activity.compose.BackHandler
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.roadsos.theme.RoadSoSTheme

enum class BottomNavScreen {
    HOME,
    SERVICES,
    AI,
    CONTACTS,
    SERVICE_DETAIL,
    ADD_CONTACT,
    PROFILE,
    PERMISSIONS,
    FULL_MAP
}

@Composable
fun MainContainerScreen(
    onLogout: () -> Unit
) {

    var currentScreen by remember {
        mutableStateOf(BottomNavScreen.HOME)
    }
    BackHandler(

        enabled =
            currentScreen != BottomNavScreen.HOME
    ) {

        currentScreen =
            BottomNavScreen.HOME
    }

    var selectedService by remember {
        mutableStateOf<EmergencyService?>(null)
    }

    // CONTACTS VIEWMODEL

    val contactsViewModel: ContactsViewModel = viewModel()
    val contacts by contactsViewModel.contacts.collectAsState()
    val toastMessage by contactsViewModel.toastMessage.collectAsState()
    val context = LocalContext.current

    // Fetch contacts when screen first loads
    LaunchedEffect(Unit) {
        contactsViewModel.fetchContacts()
    }

    // Show toast messages from ViewModel
    LaunchedEffect(toastMessage) {
        toastMessage?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            contactsViewModel.clearToast()
        }
    }
    
    var initialMapCategory by remember { mutableStateOf<PlaceCategory?>(null) }

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        when (currentScreen) {

            // HOME

            BottomNavScreen.HOME -> {

                HomeScreen(
                    currentScreen = currentScreen,

                    onTabSelected = {
                        currentScreen = it
                    },

                    onMapClick = { category ->
                        initialMapCategory = category
                        currentScreen = BottomNavScreen.FULL_MAP
                    }
                )
            }

            // SERVICES

            BottomNavScreen.SERVICES -> {

                ServicesScreen(
                    currentScreen = currentScreen,

                    onTabSelected = {
                        currentScreen = it
                    },

                    onServiceClick = { service ->

                        selectedService = service

                        currentScreen =
                            BottomNavScreen.SERVICE_DETAIL
                    }
                )
            }

            // SERVICE DETAIL

            BottomNavScreen.SERVICE_DETAIL -> {

                selectedService?.let { service ->

                    ServiceDetailScreen(
                        service = service,

                        currentScreen = currentScreen,

                        onTabSelected = {
                            currentScreen = it
                        },

                        onBack = {

                            currentScreen =
                                BottomNavScreen.SERVICES
                        }
                    )
                }
            }

            // AI SCREEN

            BottomNavScreen.AI -> {

                AIAssistantScreen(

                    onBack = {
                        currentScreen = BottomNavScreen.HOME
                    }
                )
            }

            // CONTACTS SCREEN

            BottomNavScreen.CONTACTS -> {

                ContactsScreen(
                    currentScreen = currentScreen,

                    onTabSelected = {
                        currentScreen = it
                    },

                    contacts = contacts,

                    onAddContact = {

                        if (contacts.size >= 5) {
                            Toast.makeText(
                                context,
                                "Maximum 5 emergency contacts allowed",
                                Toast.LENGTH_SHORT
                            ).show()
                        } else {
                            currentScreen =
                                BottomNavScreen.ADD_CONTACT
                        }
                    },

                    onDeleteContact = { contact ->

                        contactsViewModel.deleteContact(contact)
                    }
                )
            }

            // ADD CONTACT SCREEN

            BottomNavScreen.ADD_CONTACT -> {

                AddContactScreen(

                    onBack = {

                        currentScreen =
                            BottomNavScreen.CONTACTS
                    },

                    onSave = { newContact ->

                        contactsViewModel.addContact(newContact) {
                            currentScreen =
                                BottomNavScreen.CONTACTS
                        }
                    }
                )
            }
            BottomNavScreen.PROFILE -> {

                ProfileScreen(

                    onBack = {

                        currentScreen =
                            BottomNavScreen.HOME
                    },

                    onOpenPermissions = {

                        currentScreen =
                            BottomNavScreen.PERMISSIONS
                    },

                    onLogout = {

                        onLogout()
                    }
                )
            }
            BottomNavScreen.PERMISSIONS -> {

                PermissionScreen(

                    onBack = {

                        currentScreen =
                            BottomNavScreen.PROFILE
                    },

                    onContinue = {

                        currentScreen =
                           BottomNavScreen.HOME
                    }
                )
            }
            
            BottomNavScreen.FULL_MAP -> {
                com.example.roadsos.screens.home.FullMapScreen(
                    initialCategory = initialMapCategory,
                    onBack = {
                        currentScreen = BottomNavScreen.HOME
                        initialMapCategory = null
                    }
                )
            }
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun MainContainerScreenPreview() {
    RoadSoSTheme {
        MainContainerScreen(onLogout = {})
    }
}