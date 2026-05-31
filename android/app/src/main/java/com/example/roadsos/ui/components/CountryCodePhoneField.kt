package com.example.roadsos.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite

@Composable
fun CountryCodePhoneField(
    phoneNumber: String,
    countryCode: String,
    onPhoneNumberChange: (String) -> Unit,
    onCountryCodeChange: (String) -> Unit
) {

    Row(
        modifier = Modifier.fillMaxWidth()
    ) {

        // COUNTRY CODE

        OutlinedTextField(
            value = countryCode,
            onValueChange = onCountryCodeChange,

            modifier = Modifier.width(85.dp),

            singleLine = true,

            placeholder = {
                Text(
                    "+91",
                    color = TextGray
                )
            },

            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Phone
            ),

            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = Color(0xFF161B24),
                unfocusedContainerColor = Color(0xFF161B24),
                focusedBorderColor = PrimaryRed,
                unfocusedBorderColor = Color.Transparent,
                focusedTextColor = TextWhite,
                unfocusedTextColor = TextWhite,
                cursorColor = PrimaryRed
            ),

            shape = RoundedCornerShape(22.dp)
        )

        Spacer(
            modifier = Modifier.width(8.dp)
        )

        // PHONE NUMBER

        OutlinedTextField(
            value = phoneNumber,
            onValueChange = onPhoneNumberChange,

            modifier = Modifier.weight(1f),

            singleLine = true,

            leadingIcon = {

                Icon(
                    imageVector = Icons.Default.Phone,
                    contentDescription = null,
                    tint = PrimaryRed
                )
            },

            placeholder = {

                Text(
                    text = "Phone Number",
                    color = TextGray
                )
            },

            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Phone
            ),

            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = Color(0xFF161B24),
                unfocusedContainerColor = Color(0xFF161B24),
                focusedBorderColor = PrimaryRed,
                unfocusedBorderColor = Color.Transparent,
                focusedTextColor = TextWhite,
                unfocusedTextColor = TextWhite,
                cursorColor = PrimaryRed
            ),

            shape = RoundedCornerShape(22.dp)
        )
    }
}