package com.example.roadsos

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import com.google.android.gms.location.LocationServices

object LocationUtils {

    @SuppressLint("MissingPermission")
    fun getCurrentLocation(
        context: Context,
        onLocationReceived: (Double, Double) -> Unit
    ) {

        if (
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {

            onLocationReceived(0.0, 0.0)
            return
        }

        val fusedLocationClient =
            LocationServices.getFusedLocationProviderClient(context)

        fusedLocationClient.lastLocation
            .addOnSuccessListener { location ->

                if (location != null) {

                    onLocationReceived(
                        location.latitude,
                        location.longitude
                    )

                } else {

                    onLocationReceived(0.0, 0.0)
                }
            }
            .addOnFailureListener {

                onLocationReceived(0.0, 0.0)
            }
    }
}