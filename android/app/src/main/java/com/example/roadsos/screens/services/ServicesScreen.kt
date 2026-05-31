package com.example.roadsos.screens.services

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.LocalPolice
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.screens.home.BottomNavBar
import com.example.roadsos.screens.navigation.BottomNavScreen
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import com.example.roadsos.models.EmergencyService
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.platform.LocalContext
import com.example.roadsos.LocationUtils
import com.example.roadsos.utils.EmergencyNumbersProvider

import com.example.roadsos.viewmodel.ServiceViewModel

import com.example.roadsos.ui.components.EmptyStateCard
import androidx.compose.ui.tooling.preview.Preview
import com.example.roadsos.theme.RoadSoSTheme


//data class EmergencyService(
//    val name: String,
//    val type: String,
//    val distance: String,
//    val eta: String,
//    val rating: String,
//    val icon: ImageVector
//)

@Composable
fun ServicesScreen(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    onServiceClick: (EmergencyService) -> Unit,
    viewModel: ServiceViewModel = viewModel()
) {

    val services by viewModel.services.collectAsState()
    val searchText by viewModel.searchText.collectAsState()
    val selectedFilter by viewModel.selectedFilter.collectAsState()
    
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        LocationUtils.getCurrentLocation(context) { lat, lon ->
            if (lat != 0.0 && lon != 0.0) {
                viewModel.fetchNearbyServices(lat, lon, context)
            }
        }
    }

    ServicesScreenContent(
        currentScreen = currentScreen,
        onTabSelected = onTabSelected,
        onServiceClick = onServiceClick,
        services = services,
        searchText = searchText,
        selectedFilter = selectedFilter,
        onSearchChange = { viewModel.setSearchText(it) },
        onFilterChange = { viewModel.setFilter(it) }
    )
}

@Composable
fun ServicesScreenContent(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    onServiceClick: (EmergencyService) -> Unit,
    services: List<EmergencyService>,
    searchText: String,
    selectedFilter: String,
    onSearchChange: (String) -> Unit,
    onFilterChange: (String) -> Unit
) {

    // Removed local state, using hoisted state

//    val services = listOf(
//
//        EmergencyService(
//            "AIIMS Trauma Centre",
//            "Hospital",
//            "0.8 km",
//            "4 min",
//            "4.8",
//            Icons.Default.LocalHospital
//        ),
//
//        EmergencyService(
//            "City Ambulance 108",
//            "Ambulance",
//            "1.2 km",
//            "6 min",
//            "4.6",
//            Icons.Default.Call
//        ),
//
//        EmergencyService(
//            "Police Station",
//            "Police",
//            "1.5 km",
//            "5 min",
//            "4.5",
//            Icons.Default.LocalPolice
//        ),
//
//        EmergencyService(
//            "Rapid Tow Service",
//            "Towing",
//            "2.1 km",
//            "8 min",
//            "4.4",
//            Icons.Default.DirectionsCar
//        )
//    )

    val filteredServices = services.filter { service ->

        val matchesSearch =

            service.name.contains(
                searchText,
                ignoreCase = true
            )

        val matchesFilter =

            selectedFilter == "All" ||

                    service.type.equals(
                        selectedFilter,
                        ignoreCase = true
                    )

        matchesSearch && matchesFilter
    }

    val filters = listOf(
        "All",
        "Hospital",
        "Ambulance",
        "Police",
        "Towing"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
        ) {

            // FIXED HEADER

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
            ) {

                Spacer(
                    modifier =
                        Modifier.height(56.dp)
                )

                Text(
                    text = "Nearby Services",
                    color = TextWhite,
                    fontSize = 32.sp,
                    fontWeight =
                        FontWeight.Bold
                )

                Spacer(
                    modifier =
                        Modifier.height(2.dp)
                )

                Text(
                    text =
                        "Emergency help around you",

                    color =
                        TextGray,

                    fontSize =
                        15.sp
                )

                Spacer(
                    modifier =
                        Modifier.height(18.dp)
                )

                // SEARCH

                OutlinedTextField(

                    value = searchText,

                    onValueChange = {

                        onSearchChange(it)
                    },

                    modifier =
                        Modifier.fillMaxWidth(),

                    placeholder = {

                        Text(
                            text =
                                "Search services...",

                            color =
                                TextGray
                        )
                    },

                    leadingIcon = {

                        Icon(
                            imageVector =
                                Icons.Default.Search,

                            contentDescription =
                                null,

                            tint =
                                TextGray
                        )
                    },

                    singleLine = true,

                    colors =
                        OutlinedTextFieldDefaults.colors(

                            focusedContainerColor =
                                CardBackground,

                            unfocusedContainerColor =
                                CardBackground,

                            focusedBorderColor =
                                PrimaryRed,

                            unfocusedBorderColor =
                                Color.Transparent,

                            focusedTextColor =
                                TextWhite,

                            unfocusedTextColor =
                                TextWhite,

                            cursorColor =
                                PrimaryRed
                        ),

                    shape =
                        RoundedCornerShape(
                            22.dp
                        )
                )

                Spacer(
                    modifier =
                        Modifier.height(16.dp)
                )

                // FILTERS

                LazyRow {

                    items(filters) { filter ->

                        FilterChip(

                            selected =
                                selectedFilter ==
                                        filter,

                            onClick = {

                                onFilterChange(filter)
                            },

                            label = {

                                Text(filter)
                            },

                            colors =
                                FilterChipDefaults.filterChipColors(

                                    selectedContainerColor =
                                        PrimaryRed,

                                    selectedLabelColor =
                                        Color.White,

                                    containerColor =
                                        CardBackground,

                                    labelColor =
                                        TextGray
                                ),

                            modifier =
                                Modifier.padding(
                                    end = 10.dp
                                )
                        )
                    }
                }

                Spacer(
                    modifier =
                        Modifier.height(18.dp)
                )
            }

            // SCROLLABLE SERVICES LIST

            if (
                filteredServices.isEmpty()
            ) {

                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(
                            horizontal = 20.dp
                        )
                ) {

                    EmptyStateCard(

                        title =
                            "No Services Found",

                        subtitle =
                            "No nearby emergency services match your search."
                    )
                }

            } else {

                LazyColumn(

                    modifier =
                        Modifier.fillMaxSize(),

                    contentPadding =
                        PaddingValues(

                            start = 20.dp,
                            end = 20.dp,
                            bottom = 140.dp
                        )
                ) {

                    items(filteredServices) {

                            service ->

                        ServiceCard(

                            service =
                                service,

                            onClick = {

                                onServiceClick(
                                    service
                                )
                            }
                        )

                        Spacer(
                            modifier =
                                Modifier.height(
                                    16.dp
                                )
                        )
                    }
                }
            }
        }

        // BOTTOM NAV

        Box(
            modifier =
                Modifier.align(
                    Alignment.BottomCenter
                )
        ) {

            BottomNavBar(
                currentScreen =
                    currentScreen,

                onTabSelected =
                    onTabSelected,

                onSOSError = { }
            )
        }
    }
}

@Composable
fun ServiceCard(
    service: EmergencyService,
    onClick: () -> Unit
) {

    Card(
        onClick = onClick,

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(28.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),

            verticalAlignment = Alignment.CenterVertically
        ) {

            // ICON

            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(RoundedCornerShape(20.dp))
                    .background(
                        PrimaryRed.copy(alpha = 0.12f)
                    ),

                contentAlignment = Alignment.Center
            ) {

                Icon(
                    imageVector = when(service.type.lowercase()) {
                        "hospital"->
                            Icons.Default.LocalHospital

                        "ambulance"->
                            Icons.Default.Call

                        "police"->
                            Icons.Default.LocalPolice

                        else ->
                            Icons.Default.DirectionsCar
                    },
                    contentDescription = null,
                    tint = PrimaryRed,
                    modifier = Modifier.size(30.dp)
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            // INFO
            Column(
                modifier = Modifier.weight(1f)
            ) {

                Text(
                    text = service.name,
                    color = TextWhite,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = service.type,
                    color = TextGray,
                    fontSize = 13.sp
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    InfoPill("${service.distance_km}km")

                    Spacer(modifier = Modifier.width(8.dp))

                    InfoPill("Live")

                    Spacer(modifier = Modifier.width(8.dp))

                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {

                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            tint = Color(0xFFFFC107),
                            modifier = Modifier.size(16.dp)
                        )

                        Spacer(modifier = Modifier.width(4.dp))

                        Text(
                            text = service.rating.toString(),
                            color = TextGray,
                            fontSize = 12.sp
                        )
                    }
                }
            }

            // CALL BUTTON

            val context = LocalContext.current

            IconButton(
                onClick = {
                    val cleaned = EmergencyNumbersProvider.cleanPhoneNumber(service.phone)
                    if (cleaned.isEmpty()) {
                        android.widget.Toast.makeText(context, "Phone number not available for this location.", android.widget.Toast.LENGTH_SHORT).show()
                    } else {
                        try {
                            if (androidx.core.content.ContextCompat.checkSelfPermission(
                                    context, android.Manifest.permission.CALL_PHONE
                                ) == android.content.pm.PackageManager.PERMISSION_GRANTED
                            ) {
                                context.startActivity(
                                    android.content.Intent(android.content.Intent.ACTION_CALL, android.net.Uri.parse("tel:$cleaned"))
                                )
                            } else {
                                context.startActivity(
                                    android.content.Intent(android.content.Intent.ACTION_DIAL, android.net.Uri.parse("tel:$cleaned"))
                                )
                            }
                        } catch (e: Exception) {
                            context.startActivity(
                                android.content.Intent(android.content.Intent.ACTION_DIAL, android.net.Uri.parse("tel:$cleaned"))
                            )
                        }
                    }
                },

                modifier = Modifier
                    .clip(CircleShape)
                    .background(
                        PrimaryRed.copy(alpha = 0.15f)
                    )
            ) {

                Icon(
                    imageVector = Icons.Default.Call,
                    contentDescription = null,
                    tint = PrimaryRed
                )
            }
        }
    }
}

@Composable
fun InfoPill(text: String) {

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(14.dp))
            .background(Color(0xFF182232))
            .padding(
                horizontal = 10.dp,
                vertical = 5.dp
            )
    ) {

        Text(
            text = text,
            color = TextGray,
            fontSize = 11.sp
        )
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun ServicesScreenPreview() {

    val previewServices = listOf(
        EmergencyService(
            id = 1,
            name = "City Ambulance 108",
            type = "Ambulance",
            phone = "108",
            address = "Main Road",
            city = "Guwahati",
            latitude = 26.1445,
            longitude = 91.7362,
            rating = 4.6,
            distance_km = 1.2
        ),
        EmergencyService(
            id = 2,
            name = "AIIMS Trauma Centre",
            type = "Hospital",
            phone = "+91 9876543210",
            address = "Central Avenue",
            city = "Guwahati",
            latitude = 26.1458,
            longitude = 91.7381,
            rating = 4.8,
            distance_km = 0.8
        )
    )

    RoadSoSTheme {
        ServicesScreenContent(
            currentScreen = BottomNavScreen.SERVICES,
            onTabSelected = {},
            onServiceClick = {},
            services = previewServices,
            searchText = "",
            selectedFilter = "All",
            onSearchChange = {},
            onFilterChange = {}
        )
    }
}