package com.example.roadsos.viewmodel

import android.app.Activity
import android.content.Context
import android.util.Log
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetCredentialResponse
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.firebase.FirebaseException
import com.google.firebase.auth.AuthCredential
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider
import com.google.firebase.auth.PhoneAuthCredential
import com.google.firebase.auth.PhoneAuthOptions
import com.google.firebase.auth.PhoneAuthProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import java.util.concurrent.TimeUnit

sealed class AuthState {
    object Idle : AuthState()
    object Loading : AuthState()
    data class OtpSent(val verificationId: String) : AuthState()
    object Success : AuthState()
    data class Error(val message: String) : AuthState()
}

class AuthViewModel : ViewModel() {

    private val auth = FirebaseAuth.getInstance()
    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private var storedVerificationId: String? = null

    // REPLACE THIS WITH YOUR WEB CLIENT ID from google-services.json oauth_client (type 3)
    private val WEB_CLIENT_ID = "921990792818-3buvhpr493hnm10icog1s61sujcb1bfa.apps.googleusercontent.com"

    init {
        auth.firebaseAuthSettings.forceRecaptchaFlowForTesting(false)
    }

    fun sendVerificationCode(phone: String, activity: Activity, isSignup: Boolean, name: String) {
        _authState.value = AuthState.Loading

        val options = PhoneAuthOptions.newBuilder(auth)
            .setPhoneNumber(phone)
            .setTimeout(60L, TimeUnit.SECONDS)
            .setActivity(activity)
            .setCallbacks(object : PhoneAuthProvider.OnVerificationStateChangedCallbacks() {
                override fun onVerificationCompleted(credential: PhoneAuthCredential) {
                    // Auto-retrieval or instant verification
                    signInWithCredential(credential, isSignup, name)
                }

                override fun onVerificationFailed(e: FirebaseException) {
                    _authState.value = AuthState.Error(e.message ?: "Verification failed")
                }

                override fun onCodeSent(
                    verificationId: String,
                    token: PhoneAuthProvider.ForceResendingToken
                ) {
                    storedVerificationId = verificationId
                    _authState.value = AuthState.OtpSent(verificationId)
                }
            }).build()

        PhoneAuthProvider.verifyPhoneNumber(options)
    }

    fun verifyOtp(code: String, isSignup: Boolean, name: String) {
        val verificationId = storedVerificationId
        if (verificationId == null) {
            _authState.value = AuthState.Error("Verification ID is missing. Request OTP again.")
            return
        }

        _authState.value = AuthState.Loading
        val credential = PhoneAuthProvider.getCredential(verificationId, code)
        signInWithCredential(credential, isSignup, name)
    }

    private fun signInWithCredential(credential: AuthCredential, isSignup: Boolean, name: String) {
        viewModelScope.launch {
            try {
                val result = auth.signInWithCredential(credential).await()
                val uid = result.user?.uid
                if (uid != null) {
                    val firestore = com.google.firebase.firestore.FirebaseFirestore.getInstance()
                    val doc = firestore.collection("users").document(uid).get().await()
                    
                    if (isSignup) {
                        if (!doc.exists()) {
                            val newProfile = hashMapOf(
                                "name" to name,
                                "phone" to (result.user?.phoneNumber ?: ""),
                                "profileUrl" to ""
                            )
                            firestore.collection("users").document(uid).set(newProfile).await()
                        }
                        _authState.value = AuthState.Success
                        fetchIdToken()
                    } else {
                        if (!doc.exists()) {
                            result.user?.delete()?.await()
                            auth.signOut()
                            _authState.value = AuthState.Error("Account not found. Please sign up first.")
                        } else {
                            _authState.value = AuthState.Success
                            fetchIdToken()
                        }
                    }
                } else {
                    _authState.value = AuthState.Error("Sign in failed")
                }
            } catch (e: Exception) {
                _authState.value = AuthState.Error(e.message ?: "Sign in failed")
            }
        }
    }

    fun signInWithGoogle(context: Context, isSignup: Boolean, name: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            try {
                val credentialManager = CredentialManager.create(context)
                
                val googleIdOption = GetGoogleIdOption.Builder()
                    .setFilterByAuthorizedAccounts(false)
                    .setServerClientId(WEB_CLIENT_ID)
                    .setAutoSelectEnabled(true)
                    .build()

                val request = GetCredentialRequest.Builder()
                    .addCredentialOption(googleIdOption)
                    .build()

                val result = credentialManager.getCredential(context, request)
                handleGoogleSignInResult(result, isSignup, name)

            } catch (e: Exception) {
                _authState.value = AuthState.Error(e.message ?: "Google Sign-In failed")
            }
        }
    }

    private fun handleGoogleSignInResult(result: GetCredentialResponse, isSignup: Boolean, name: String) {
        val credential = result.credential
        if (credential is CustomCredential && credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL) {
            try {
                val googleIdTokenCredential = GoogleIdTokenCredential.createFrom(credential.data)
                val firebaseCredential = GoogleAuthProvider.getCredential(googleIdTokenCredential.idToken, null)
                
                viewModelScope.launch {
                    try {
                        val authResult = auth.signInWithCredential(firebaseCredential).await()
                        val uid = authResult.user?.uid
                        if (uid != null) {
                            val firestore = com.google.firebase.firestore.FirebaseFirestore.getInstance()
                            val doc = firestore.collection("users").document(uid).get().await()
                            
                            if (isSignup) {
                                if (!doc.exists()) {
                                    val newProfile = hashMapOf(
                                        "name" to (authResult.user?.displayName ?: name),
                                        "phone" to (authResult.user?.phoneNumber ?: ""),
                                        "profileUrl" to (authResult.user?.photoUrl?.toString() ?: "")
                                    )
                                    firestore.collection("users").document(uid).set(newProfile).await()
                                }
                                _authState.value = AuthState.Success
                                fetchIdToken()
                            } else {
                                if (!doc.exists()) {
                                    authResult.user?.delete()?.await()
                                    auth.signOut()
                                    _authState.value = AuthState.Error("Account not found. Please sign up first.")
                                } else {
                                    _authState.value = AuthState.Success
                                    fetchIdToken()
                                }
                            }
                        } else {
                            _authState.value = AuthState.Error("Sign in failed")
                        }
                    } catch (e: Exception) {
                        _authState.value = AuthState.Error(e.message ?: "Firebase authentication failed")
                    }
                }
            } catch (e: Exception) {
                _authState.value = AuthState.Error("Failed to parse Google credential")
            }
        } else {
            _authState.value = AuthState.Error("Unexpected credential type")
        }
    }

    fun resetState() {
        _authState.value = AuthState.Idle
    }

    fun fetchIdToken() {
        auth.currentUser?.getIdToken(true)?.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val token = task.result?.token
                Log.e("RoadSoS_Token", "=========================================================")
                Log.e("RoadSoS_Token", "FIREBASE ID TOKEN (From AuthViewModel):")
                Log.e("RoadSoS_Token", "$token")
                Log.e("RoadSoS_Token", "=========================================================")
            } else {
                Log.e("RoadSoS_Token", "Failed to get ID token", task.exception)
            }
        }
    }
}
