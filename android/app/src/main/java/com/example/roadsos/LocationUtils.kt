package com.example.roadsos

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import androidx.core.content.ContextCompat
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

object LocationUtils {

    @SuppressLint("MissingPermission")
    fun getCurrentLocation(
        context: Context,
        onLocationReceived: (Double, Double) -> Unit
    ) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            onLocationReceived(0.0, 0.0)
            return
        }

        val fusedLocationClient = LocationServices.getFusedLocationProviderClient(context)

        // Try to get fresh location instead of relying on cached lastLocation
        fusedLocationClient.getCurrentLocation(com.google.android.gms.location.Priority.PRIORITY_HIGH_ACCURACY, null)
            .addOnSuccessListener { location ->
                if (location != null) {
                    onLocationReceived(location.latitude, location.longitude)
                    updateFirestoreLocation(location.latitude, location.longitude)
                    
                    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                        try {
                            com.example.roadsos.utils.PlacesSyncManager.syncNearbyServices(context, location.latitude, location.longitude)
                        } catch (e: Exception) {
                            android.util.Log.e("LocationUtils", "Failed to sync nearby services", e)
                        }
                    }
                } else {
                    // Fallback to 0.0 only if even fresh location fails
                    onLocationReceived(0.0, 0.0)
                }
            }.addOnFailureListener { onLocationReceived(0.0, 0.0) }

        // Continuous updates if displacement > 15km (15000 meters)
        val locationRequest = com.google.android.gms.location.LocationRequest.Builder(
            com.google.android.gms.location.Priority.PRIORITY_HIGH_ACCURACY, 10000
        ).setMinUpdateDistanceMeters(15000f).build()

        val locationCallback = object : com.google.android.gms.location.LocationCallback() {
            override fun onLocationResult(locationResult: com.google.android.gms.location.LocationResult) {
                locationResult.lastLocation?.let { location ->
                    updateFirestoreLocation(location.latitude, location.longitude)
                    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                        com.example.roadsos.utils.PlacesSyncManager.syncNearbyServices(context, location.latitude, location.longitude)
                        kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                            onLocationReceived(location.latitude, location.longitude)
                        }
                    }
                }
            }
        }
        fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, android.os.Looper.getMainLooper())
    }

    /**
     * Check if GPS provider is currently enabled on the device
     */
    fun isGpsEnabled(context: Context): Boolean {
        return try {
            val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
        } catch (e: Exception) {
            false
        }
    }

    private fun updateFirestoreLocation(lat: Double, lng: Double) {
        val user = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser
        if (user != null) {
            val locationData = mapOf(
                "latitude" to lat,
                "longitude" to lng,
                "last_location_update" to System.currentTimeMillis()
            )
            val data = mapOf(
                "location" to locationData
            )
            com.google.firebase.firestore.FirebaseFirestore.getInstance()
                .collection("users").document(user.uid)
                .set(data, com.google.firebase.firestore.SetOptions.merge())
        }
    }
}