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

    fun fetchNearbyServices(
        lat: Double = 26.1445,
        lon: Double = 91.7362
    ) {

        viewModelScope.launch {

            try {

                val response =
                    repository.getNearbyServices(
                        lat,
                        lon,
                        5000,
                        null
                    )

                response.body()?.let {
                    _services.value = it.data
                }

            } catch (e: Exception) {

                e.printStackTrace()
            }
        }
    }
}