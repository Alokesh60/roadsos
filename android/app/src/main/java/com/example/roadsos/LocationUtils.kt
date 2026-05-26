package com.example.roadsos

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import androidx.core.content.ContextCompat
import com.google.android.gms.location.LocationServices

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

        // Initial location
        fusedLocationClient.lastLocation.addOnSuccessListener { location ->
            if (location != null) onLocationReceived(location.latitude, location.longitude)
            else onLocationReceived(0.0, 0.0)
        }.addOnFailureListener { onLocationReceived(0.0, 0.0) }

        // Continuous updates if displacement > 10km (10000 meters)
        val locationRequest = com.google.android.gms.location.LocationRequest.Builder(
            com.google.android.gms.location.Priority.PRIORITY_HIGH_ACCURACY, 10000
        ).setMinUpdateDistanceMeters(10000f).build()

        val locationCallback = object : com.google.android.gms.location.LocationCallback() {
            override fun onLocationResult(locationResult: com.google.android.gms.location.LocationResult) {
                locationResult.lastLocation?.let { location ->
                    onLocationReceived(location.latitude, location.longitude)
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
}