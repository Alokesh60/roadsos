package com.example.roadsos.utils

import android.content.Context
import android.telephony.SmsManager
import android.util.Log
import com.example.roadsos.database.AppDatabase
import com.example.roadsos.models.NearbyPlaceJson
import com.example.roadsos.models.SosRequest
import com.example.roadsos.network.ApiClient
import com.example.roadsos.network.ApiService
import com.example.roadsos.LocationUtils
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

object EmergencyDispatcher {

    fun dispatchEmergency(context: Context, source: String, onComplete: ((com.example.roadsos.models.SosResponse?) -> Unit)? = null) {
        val db = AppDatabase.getDatabase(context)
        val auth = FirebaseAuth.getInstance()
        val appContext = context.applicationContext

        LocationUtils.getCurrentLocation(appContext) { lat, lng ->
            CoroutineScope(Dispatchers.IO).launch {
                val hasInternet = NetworkUtils.isNetworkAvailable(appContext)

                // ALWAYS send SMS to personal emergency contacts first, regardless of internet connection.
                // The backend does not have access to these local contacts, so the app must do it.
                dispatchEmergencySms(appContext, lat, lng, auth, db)

                if (!hasInternet) {
                    onComplete?.invoke(null)
                } else {
                    // Send a minimal request to the backend just to trigger push notifications, removing the heavy AI data payload.
                    val request = SosRequest(
                        message = "Emergency SOS triggered",
                        latitude = lat,
                        longitude = lng,
                        country = "India",
                        nearby_services = emptyMap(),
                        nearby_places = emptyList(),
                        source = source,
                        offline_mode = false
                    )

                    val apiService = ApiClient.retrofit.create(ApiService::class.java)
                    try {
                        val response = apiService.triggerSos(request)
                        if (response.isSuccessful) {
                            Log.d("EmergencyDispatcher", "Backend SOS triggered: ${response.body()?.message}")
                            onComplete?.invoke(response.body())
                        } else {
                            Log.e("EmergencyDispatcher", "Failed to trigger backend SOS: ${response.errorBody()?.string()}")
                            onComplete?.invoke(null)
                        }
                    } catch (e: Exception) {
                        Log.e("EmergencyDispatcher", "Exception triggering backend SOS", e)
                        onComplete?.invoke(null)
                    }
                }
            }
        }
    }

    private fun dispatchEmergencySms(context: Context, lat: Double, lng: Double, auth: FirebaseAuth, db: AppDatabase) {
        val userName = auth.currentUser?.displayName ?: "a RoadSOS user"
        val fallbackNumbers = EmergencyNumbersProvider.getEmergencyNumbers(context, lat, lng)
        val localPolice = db.nearbyServiceDao().getServicesByCategorySync("police").firstOrNull()?.phone ?: ""
        val police = if (EmergencyNumbersProvider.isValidPhoneNumber(localPolice)) localPolice else fallbackNumbers.police

        val localAmbulance = db.nearbyServiceDao().getServicesByCategorySync("ambulance").firstOrNull()?.phone ?: ""
        val ambulance = if (EmergencyNumbersProvider.isValidPhoneNumber(localAmbulance)) localAmbulance else fallbackNumbers.ambulance

        val localHospital = db.nearbyServiceDao().getServicesByCategorySync("hospital").firstOrNull()?.phone ?: ""
        val hospital = if (EmergencyNumbersProvider.isValidPhoneNumber(localHospital)) localHospital else fallbackNumbers.hospital

        val localTowing = db.nearbyServiceDao().getServicesByCategorySync("garage").firstOrNull()?.phone ?: ""
        val towing = if (EmergencyNumbersProvider.isValidPhoneNumber(localTowing)) localTowing else fallbackNumbers.towing

        val smsManager = SmsManager.getDefault()
        val message = "SOS! I am $userName in danger! Loc: https://maps.google.com/?q=$lat,$lng . Nearby Police:$police, Amb:$ambulance, Hosp:$hospital, Tow:$towing. Call them ASAP!"

        val contacts = db.emergencyContactDao().getAllContacts()
        for (contact in contacts) {
            val fullNumber = "${contact.countryCode}${contact.phone}"
            try {
                val parts = smsManager.divideMessage(message)
                smsManager.sendMultipartTextMessage(fullNumber, null, parts, null, null)
                Log.d("EmergencyDispatcher", "SOS SMS sent to $fullNumber")
            } catch (e: Exception) {
                Log.e("EmergencyDispatcher", "Failed to send SMS to $fullNumber", e)
            }
        }
    }
}
