package com.example.roadsos.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.roadsos.database.AppDatabase
import com.example.roadsos.models.ChatRequest
import com.example.roadsos.models.NearbyPlaceJson
import com.example.roadsos.repository.AIRepository
import com.example.roadsos.LocationUtils
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.Dispatchers

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

class AIViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AIRepository()
    private val db = AppDatabase.getDatabase(application)
    private val auth = FirebaseAuth.getInstance()

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _placesSynced = MutableStateFlow(false)
    val placesSynced: StateFlow<Boolean> = _placesSynced

    private var sessionId: String = java.util.UUID.randomUUID().toString()
    private var lastLat: Double = 0.0
    private var lastLng: Double = 0.0

    init {
        addMessage(ChatMessage(text = "Hi there! I'm your AI Emergency Assistant. How can I help you today?", isUser = false))
    }

    fun syncPlaces() {
        if (_placesSynced.value) return
        
        viewModelScope.launch(Dispatchers.IO) {
            val context = getApplication<Application>()
            
            LocationUtils.getCurrentLocation(context) { lat, lng ->
                lastLat = lat
                lastLng = lng
                _placesSynced.value = true
            }
        }
    }

    fun sendMessage(text: String) {
        if (text.isBlank()) return

        addMessage(ChatMessage(text = text, isUser = true))
        _isLoading.value = true

        viewModelScope.launch(Dispatchers.IO) {
            val user = auth.currentUser
            if (user == null) {
                addMessage(ChatMessage(text = "Please log in to use the AI assistant.", isUser = false))
                _isLoading.value = false
                return@launch
            }

            val allLocalPlaces = db.nearbyServiceDao().getAllServicesSync()
            val nearbyPlacesJson = allLocalPlaces.map { p ->
                NearbyPlaceJson(
                    id = p.id,
                    category = p.category,
                    name = p.name,
                    phone = p.phone,
                    latitude = p.latitude,
                    longitude = p.longitude,
                    rating = p.rating,
                    isOpenNow = p.isOpenNow,
                    distanceMeters = p.distanceMeters,
                    estimatedEtaMinutes = p.estimatedEtaMinutes
                )
            }

            val fallbackNumbers = com.example.roadsos.utils.EmergencyNumbersProvider.getEmergencyNumbers(getApplication(), lastLat, lastLng)
            val localPolice = db.nearbyServiceDao().getServicesByCategorySync("police").firstOrNull()?.phone ?: ""
            val police = if (com.example.roadsos.utils.EmergencyNumbersProvider.isValidPhoneNumber(localPolice)) localPolice else fallbackNumbers.police

            val localAmbulance = db.nearbyServiceDao().getServicesByCategorySync("ambulance").firstOrNull()?.phone ?: ""
            val ambulance = if (com.example.roadsos.utils.EmergencyNumbersProvider.isValidPhoneNumber(localAmbulance)) localAmbulance else fallbackNumbers.ambulance

            val localHospital = db.nearbyServiceDao().getServicesByCategorySync("hospital").firstOrNull()?.phone ?: ""
            val hospital = if (com.example.roadsos.utils.EmergencyNumbersProvider.isValidPhoneNumber(localHospital)) localHospital else fallbackNumbers.hospital

            val localTowing = db.nearbyServiceDao().getServicesByCategorySync("garage").firstOrNull()?.phone ?: ""
            val towing = if (com.example.roadsos.utils.EmergencyNumbersProvider.isValidPhoneNumber(localTowing)) localTowing else fallbackNumbers.towing

            val chatContext = com.example.roadsos.models.ChatContext(
                lat = lastLat,
                lng = lastLng,
                nearest_police_phone = police,
                nearest_ambulance_phone = ambulance,
                nearest_hospital_phone = hospital,
                nearest_towing_phone = towing,
                is_sos_active = false,
                nearby_places = nearbyPlacesJson
            )

            val history = _messages.value.map { msg ->
                com.example.roadsos.models.ChatMessage(
                    role = if (msg.isUser) "user" else "model",
                    content = msg.text
                )
            }

            val request = ChatRequest(
                session_id = sessionId,
                user_message = text,
                context = chatContext,
                history = history
            )
            val result = repository.sendChatMessage(request)

            if (result.isSuccess) {
                addMessage(ChatMessage(text = result.getOrNull() ?: "I couldn't process that.", isUser = false))
            } else {
                addMessage(ChatMessage(text = "Sorry, I am having trouble connecting to the network.", isUser = false))
            }
            
            _isLoading.value = false
        }
    }

    private fun addMessage(message: ChatMessage) {
        _messages.value = _messages.value + message
    }
}
