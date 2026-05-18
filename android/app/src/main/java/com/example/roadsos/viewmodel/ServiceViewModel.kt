package com.example.roadsos.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

import com.example.roadsos.models.EmergencyService
import com.example.roadsos.repository.ServiceRepository

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class ServiceViewModel : ViewModel() {

    private val repository =
        ServiceRepository()

    private val _services =
        MutableStateFlow<List<EmergencyService>>(emptyList())

    val services:
            StateFlow<List<EmergencyService>>
            = _services

    fun fetchNearbyServices() {

        viewModelScope.launch {

            try {

                val response =
                    repository.getNearbyServices(
                        lat = 26.1445,
                        lon = 91.7362,
                        radius = 10,
                        type = "hospital"
                    )

                if (response.isSuccessful) {

                    _services.value =
                        response.body()?.data
                            ?: emptyList()
                }

            } catch (e: Exception) {

                e.printStackTrace()
            }
        }
    }
}