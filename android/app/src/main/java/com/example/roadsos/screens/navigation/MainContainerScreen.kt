package com.example.roadsos.screens.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.example.roadsos.screens.ai.AIAssistantScreen
import com.example.roadsos.screens.contacts.AddContactScreen
import com.example.roadsos.screens.contacts.ContactsScreen
import com.example.roadsos.screens.contacts.EmergencyContact
import com.example.roadsos.screens.home.HomeScreen
import com.example.roadsos.screens.services.EmergencyService
import com.example.roadsos.screens.services.ServiceDetailScreen
import com.example.roadsos.screens.services.ServicesScreen
import com.example.roadsos.screens.profile.ProfileScreen
import com.example.roadsos.screens.permissions.PermissionScreen
import androidx.activity.compose.BackHandler

enum class BottomNavScreen {
    HOME,
    SERVICES,
    AI,
    CONTACTS,
    SERVICE_DETAIL,
    ADD_CONTACT,
    PROFILE,
    PERMISSIONS
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

    // CONTACTS STATE

    var contacts by remember {

        mutableStateOf(

            listOf(

                EmergencyContact(
                    name = "Rahul Sharma",
                    relation = "Brother",
                    number = "+91 9876543210",
                    priority = "Primary"
                ),

                EmergencyContact(
                    name = "Ananya Das",
                    relation = "Friend",
                    number = "+91 9123456780",
                    priority = "Secondary"
                ),

                EmergencyContact(
                    name = "Dr. Mehta",
                    relation = "Family Doctor",
                    number = "+91 9988776655",
                    priority = "Medical"
                ),

                EmergencyContact(
                    name = "Police Helpline",
                    relation = "Emergency",
                    number = "100",
                    priority = "SOS"
                )
            )
        )
    }

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

                        currentScreen =
                            BottomNavScreen.ADD_CONTACT
                    },

                    onDeleteContact = { contact ->

                        contacts =
                            contacts.filter {
                                it != contact
                            }
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

                        contacts =
                            contacts + newContact

                        currentScreen =
                            BottomNavScreen.CONTACTS
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
                            BottomNavScreen.PROFILE
                    }
                )
            }
        }
    }
}