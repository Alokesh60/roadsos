package com.example.roadsos.utils

import android.content.Context
import android.location.Geocoder
import java.util.Locale

/**
 * Provides emergency phone numbers (Ambulance, Police, Hospital, Towing)
 * that change based on the user's geographic location (country).
 *
 * Uses reverse geocoding to determine the country from lat/lon,
 * then returns the appropriate emergency numbers for that country.
 */
object EmergencyNumbersProvider {

    data class EmergencyNumbers(
        val ambulance: String,
        val police: String,
        val hospital: String,
        val towing: String,
        val countryName: String
    )

    // Country code -> EmergencyNumbers mapping
    private val countryNumbersMap = mapOf(
        // India
        "IN" to EmergencyNumbers(
            ambulance = "108",
            police = "100",
            hospital = "104",
            towing = "1073",
            countryName = "India"
        ),
        // United States
        "US" to EmergencyNumbers(
            ambulance = "911",
            police = "911",
            hospital = "911",
            towing = "311",
            countryName = "United States"
        ),
        // United Kingdom
        "GB" to EmergencyNumbers(
            ambulance = "999",
            police = "999",
            hospital = "111",
            towing = "0800 048 0007",
            countryName = "United Kingdom"
        ),
        // Australia
        "AU" to EmergencyNumbers(
            ambulance = "000",
            police = "000",
            hospital = "000",
            towing = "131 111",
            countryName = "Australia"
        ),
        // Canada
        "CA" to EmergencyNumbers(
            ambulance = "911",
            police = "911",
            hospital = "911",
            towing = "311",
            countryName = "Canada"
        ),
        // Germany
        "DE" to EmergencyNumbers(
            ambulance = "112",
            police = "110",
            hospital = "112",
            towing = "0180 222 2222",
            countryName = "Germany"
        ),
        // France
        "FR" to EmergencyNumbers(
            ambulance = "15",
            police = "17",
            hospital = "15",
            towing = "0800 08 92 92",
            countryName = "France"
        ),
        // Japan
        "JP" to EmergencyNumbers(
            ambulance = "119",
            police = "110",
            hospital = "119",
            towing = "#8139",
            countryName = "Japan"
        ),
        // Brazil
        "BR" to EmergencyNumbers(
            ambulance = "192",
            police = "190",
            hospital = "192",
            towing = "193",
            countryName = "Brazil"
        ),
        // South Africa
        "ZA" to EmergencyNumbers(
            ambulance = "10177",
            police = "10111",
            hospital = "10177",
            towing = "0861 040 404",
            countryName = "South Africa"
        ),
        // UAE
        "AE" to EmergencyNumbers(
            ambulance = "998",
            police = "999",
            hospital = "998",
            towing = "800 4900",
            countryName = "UAE"
        ),
        // China
        "CN" to EmergencyNumbers(
            ambulance = "120",
            police = "110",
            hospital = "120",
            towing = "122",
            countryName = "China"
        ),
        // Russia
        "RU" to EmergencyNumbers(
            ambulance = "103",
            police = "102",
            hospital = "103",
            towing = "112",
            countryName = "Russia"
        ),
        // European countries (EU standard 112)
        "IT" to EmergencyNumbers(ambulance = "112", police = "112", hospital = "118", towing = "803 116", countryName = "Italy"),
        "ES" to EmergencyNumbers(ambulance = "112", police = "112", hospital = "112", towing = "900 123 505", countryName = "Spain"),
        "NL" to EmergencyNumbers(ambulance = "112", police = "112", hospital = "112", towing = "088 269 2888", countryName = "Netherlands"),
        "SE" to EmergencyNumbers(ambulance = "112", police = "112", hospital = "1177", towing = "020 912 912", countryName = "Sweden"),
        // Singapore
        "SG" to EmergencyNumbers(ambulance = "995", police = "999", hospital = "995", towing = "1800 225 5582", countryName = "Singapore"),
        // Malaysia
        "MY" to EmergencyNumbers(ambulance = "999", police = "999", hospital = "999", towing = "1800 880 808", countryName = "Malaysia"),
        // Pakistan
        "PK" to EmergencyNumbers(ambulance = "115", police = "15", hospital = "115", towing = "112", countryName = "Pakistan"),
        // Bangladesh
        "BD" to EmergencyNumbers(ambulance = "199", police = "999", hospital = "199", towing = "999", countryName = "Bangladesh"),
        // Sri Lanka
        "LK" to EmergencyNumbers(ambulance = "110", police = "119", hospital = "110", towing = "112", countryName = "Sri Lanka"),
        // Nepal
        "NP" to EmergencyNumbers(ambulance = "102", police = "100", hospital = "102", towing = "112", countryName = "Nepal"),
    )

    // Default fallback (India)
    private val defaultNumbers = countryNumbersMap["IN"]!!

    /**
     * Determines the user's country from lat/lon via reverse geocoding
     * and returns the appropriate emergency numbers.
     */
    fun getEmergencyNumbers(
        context: Context,
        latitude: Double,
        longitude: Double
    ): EmergencyNumbers {
        if (latitude == 0.0 && longitude == 0.0) {
            return defaultNumbers
        }

        return try {
            val geocoder = Geocoder(context, Locale.getDefault())
            @Suppress("DEPRECATION")
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            if (!addresses.isNullOrEmpty()) {
                val countryCode = addresses[0].countryCode ?: "IN"
                countryNumbersMap[countryCode] ?: defaultNumbers
            } else {
                defaultNumbers
            }
        } catch (e: Exception) {
            defaultNumbers
        }
    }

    /**
     * Get the country name from lat/lon for display purposes.
     */
    fun getCountryName(
        context: Context,
        latitude: Double,
        longitude: Double
    ): String {
        if (latitude == 0.0 && longitude == 0.0) return "Detecting..."

        return try {
            val geocoder = Geocoder(context, Locale.getDefault())
            @Suppress("DEPRECATION")
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            if (!addresses.isNullOrEmpty()) {
                addresses[0].countryName ?: "Unknown"
            } else {
                "Unknown"
            }
        } catch (e: Exception) {
            "Unknown"
        }
    }

    /**
     * Validates whether a phone number string is likely dialable.
     * Returns true if the number has at least 3 digits and is not garbage.
     */
    fun isValidPhoneNumber(phone: String): Boolean {
        if (phone.isBlank()) return false
        // Strip everything except digits
        val digitsOnly = phone.replace(Regex("[^0-9]"), "")
        // Must have at least 3 digits (shortest emergency numbers are 2-3 digits)
        if (digitsOnly.length < 3) return false
        // Reject if it's all zeros
        if (digitsOnly.all { it == '0' }) return false
        // Reject if it's clearly not a phone number (e.g. too many non-digit chars)
        val nonDigitRatio = phone.count { !it.isDigit() && it != ' ' && it != '-' && it != '+' && it != '(' && it != ')' }.toFloat() / phone.length
        if (nonDigitRatio > 0.5f) return false
        return true
    }

    /**
     * Cleans a phone number for dialing by stripping invalid characters.
     * Keeps digits, +, #, and * (valid dial characters).
     */
    fun cleanPhoneNumber(phone: String): String {
        return phone.replace(Regex("[^0-9+#*]"), "")
    }
}
