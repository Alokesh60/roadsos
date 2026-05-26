package com.example.roadsos.viewmodel

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream

data class UserProfile(
    val name: String = "",
    val phone: String = "",
    val profileUrl: String = ""
)

sealed class ProfileState {
    object Idle : ProfileState()
    object Loading : ProfileState()
    data class Success(val profile: UserProfile) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

class ProfileViewModel : ViewModel() {

    private val auth = FirebaseAuth.getInstance()
    private val firestore = FirebaseFirestore.getInstance()
    private val httpClient = OkHttpClient()

    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Idle)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    fun fetchProfile() {
        val uid = auth.currentUser?.uid ?: return
        if (_profileState.value !is ProfileState.Success) {
            _profileState.value = ProfileState.Loading
        }
        viewModelScope.launch {
            try {
                val document = firestore.collection("users").document(uid).get().await()
                if (document.exists()) {
                    val profile = document.toObject(UserProfile::class.java)
                    _profileState.value = ProfileState.Success(profile ?: UserProfile())
                } else {
                    val newProfile = UserProfile(
                        name = auth.currentUser?.displayName ?: "User",
                        phone = auth.currentUser?.phoneNumber ?: "",
                        profileUrl = auth.currentUser?.photoUrl?.toString() ?: ""
                    )
                    firestore.collection("users").document(uid).set(newProfile).await()
                    _profileState.value = ProfileState.Success(newProfile)
                }
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Failed to fetch profile")
            }
        }
    }

    fun updateName(newName: String) {
        val uid = auth.currentUser?.uid ?: return
        viewModelScope.launch {
            try {
                firestore.collection("users").document(uid).update("name", newName).await()
                fetchProfile()
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Failed to update name")
            }
        }
    }

    fun updatePhone(newPhone: String) {
        val uid = auth.currentUser?.uid ?: return
        viewModelScope.launch {
            try {
                firestore.collection("users").document(uid).update("phone", newPhone).await()
                fetchProfile()
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Failed to update phone")
            }
        }
    }

    fun deleteProfilePicture() {
        val uid = auth.currentUser?.uid ?: return
        viewModelScope.launch {
            try {
                firestore.collection("users").document(uid).update("profileUrl", "").await()
                fetchProfile()
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Failed to delete profile picture")
            }
        }
    }

    fun uploadProfilePicture(uri: Uri, context: Context) {
        val uid = auth.currentUser?.uid ?: return
        _profileState.value = ProfileState.Loading
        viewModelScope.launch {
            try {
                val file = getFileFromUri(uri, context)
                if (file == null) {
                    _profileState.value = ProfileState.Error("Could not read image file")
                    return@launch
                }

                val imageUrl = uploadToCloudinary(file)
                if (imageUrl != null) {
                    firestore.collection("users").document(uid).update("profileUrl", imageUrl).await()
                    fetchProfile()
                } else {
                    _profileState.value = ProfileState.Error("Upload failed")
                }
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Error uploading image")
            }
        }
    }

    private suspend fun uploadToCloudinary(file: File): String? = withContext(Dispatchers.IO) {
        val cloudName = "dcgfvut95"
        val uploadPreset = "Roadsos"

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.name, file.asRequestBody("image/*".toMediaTypeOrNull()))
            .addFormDataPart("upload_preset", uploadPreset)
            .addFormDataPart("folder", "profile_pic")
            .build()

        val request = Request.Builder()
            .url("https://api.cloudinary.com/v1_1/$cloudName/image/upload")
            .post(requestBody)
            .build()

        try {
            val response = httpClient.newCall(request).execute()
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                if (responseBody != null) {
                    val jsonObject = JSONObject(responseBody)
                    return@withContext jsonObject.getString("secure_url")
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return@withContext null
    }

    private suspend fun getFileFromUri(uri: Uri, context: Context): File? = withContext(Dispatchers.IO) {
        try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return@withContext null
            val tempFile = File(context.cacheDir, "temp_profile_img.jpg")
            val outputStream = FileOutputStream(tempFile)
            inputStream.copyTo(outputStream)
            inputStream.close()
            outputStream.close()
            return@withContext tempFile
        } catch (e: Exception) {
            e.printStackTrace()
            return@withContext null
        }
    }

    fun deleteAccount(onSuccess: () -> Unit, onError: (String) -> Unit) {
        val user = auth.currentUser
        if (user == null) {
            onError("User not logged in")
            return
        }
        val uid = user.uid
        viewModelScope.launch {
            try {
                // Delete user from firestore
                firestore.collection("users").document(uid).delete().await()
                // Delete auth record
                user.delete().await()
                onSuccess()
            } catch (e: Exception) {
                onError(e.message ?: "Failed to delete account")
            }
        }
    }

    fun logout() {
        auth.signOut()
    }
}
