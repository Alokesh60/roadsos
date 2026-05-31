package com.example.roadsos.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.roadsos.screens.contacts.EmergencyContact
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await

sealed class ContactsState {
    object Idle : ContactsState()
    object Loading : ContactsState()
    data class Success(val contacts: List<EmergencyContact>) : ContactsState()
    data class Error(val message: String) : ContactsState()
}

class ContactsViewModel(application: android.app.Application) : androidx.lifecycle.AndroidViewModel(application) {

    private val auth = FirebaseAuth.getInstance()
    private val firestore = FirebaseFirestore.getInstance()
    private val contactDao = com.example.roadsos.database.AppDatabase.getDatabase(application).emergencyContactDao()

    private val _contactsState = MutableStateFlow<ContactsState>(ContactsState.Idle)
    val contactsState: StateFlow<ContactsState> = _contactsState.asStateFlow()

    private val _contacts = MutableStateFlow<List<EmergencyContact>>(emptyList())
    val contacts: StateFlow<List<EmergencyContact>> = _contacts.asStateFlow()

    private val _toastMessage = MutableStateFlow<String?>(null)
    val toastMessage: StateFlow<String?> = _toastMessage.asStateFlow()

    companion object {
        private const val TAG = "ContactsViewModel"
        private const val MAX_CONTACTS = 5
    }

    fun clearToast() {
        _toastMessage.value = null
    }

    /**
     * Fetches emergency contacts from Firestore subcollection:
     * users/{uid}/emergencyContacts
     */
    fun fetchContacts() {
        val uid = auth.currentUser?.uid ?: run {
            _contactsState.value = ContactsState.Error("User not logged in")
            return
        }

        _contactsState.value = ContactsState.Loading

        viewModelScope.launch {
            try {
                val snapshot = firestore
                    .collection("users")
                    .document(uid)
                    .collection("emergencyContacts")
                    .get()
                    .await()

                val contactsList = snapshot.documents.mapNotNull { doc ->
                    try {
                        EmergencyContact(
                            id = doc.id,
                            name = doc.getString("name") ?: "",
                            relation = doc.getString("relation") ?: "",
                            number = doc.getString("number") ?: "",
                            countryCode = doc.getString("countryCode") ?: "",
                            priority = doc.getString("priority") ?: ""
                        )
                    } catch (e: Exception) {
                        Log.e(TAG, "Error parsing contact doc: ${doc.id}", e)
                        null
                    }
                }

                _contacts.value = contactsList
                _contactsState.value = ContactsState.Success(contactsList)

                // Sync to Room Database
                try {
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                        contactDao.clearAll()
                        val localContacts = contactsList.map {
                            com.example.roadsos.database.entity.LocalEmergencyContact(
                                id = it.id,
                                name = it.name,
                                phone = it.number,
                                countryCode = it.countryCode,
                                relation = it.relation,
                                priority = it.priority.toIntOrNull() ?: 99
                            )
                        }
                        contactDao.insertContacts(localContacts)
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error syncing to Room", e)
                }

            } catch (e: Exception) {
                Log.e(TAG, "Error fetching contacts", e)
                _contactsState.value = ContactsState.Error(
                    e.message ?: "Failed to fetch contacts"
                )
            }
        }
    }

    /**
     * Adds a new emergency contact to Firestore.
     * Enforces a maximum of 5 contacts per user.
     */
    fun addContact(contact: EmergencyContact, onSuccess: () -> Unit) {
        val uid = auth.currentUser?.uid ?: run {
            _toastMessage.value = "User not logged in"
            return
        }

        if (_contacts.value.size >= MAX_CONTACTS) {
            _toastMessage.value = "Maximum $MAX_CONTACTS emergency contacts allowed"
            return
        }

        _contactsState.value = ContactsState.Loading

        viewModelScope.launch {
            try {
                val contactData = hashMapOf(
                    "name" to contact.name,
                    "relation" to contact.relation,
                    "number" to contact.number,
                    "countryCode" to contact.countryCode,
                    "priority" to contact.priority
                )

                firestore
                    .collection("users")
                    .document(uid)
                    .collection("emergencyContacts")
                    .add(contactData)
                    .await()

                _toastMessage.value = "Contact saved successfully"
                fetchContacts()
                onSuccess()

            } catch (e: Exception) {
                Log.e(TAG, "Error adding contact", e)
                _contactsState.value = ContactsState.Error(
                    e.message ?: "Failed to add contact"
                )
                _toastMessage.value = "Failed to save contact"
            }
        }
    }

    /**
     * Deletes an emergency contact from Firestore by document ID.
     */
    fun deleteContact(contact: EmergencyContact) {
        val uid = auth.currentUser?.uid ?: run {
            _toastMessage.value = "User not logged in"
            return
        }

        if (contact.id.isEmpty()) {
            _toastMessage.value = "Invalid contact"
            return
        }

        _contactsState.value = ContactsState.Loading

        viewModelScope.launch {
            try {
                firestore
                    .collection("users")
                    .document(uid)
                    .collection("emergencyContacts")
                    .document(contact.id)
                    .delete()
                    .await()

                _toastMessage.value = "Contact deleted"
                fetchContacts()

            } catch (e: Exception) {
                Log.e(TAG, "Error deleting contact", e)
                _contactsState.value = ContactsState.Error(
                    e.message ?: "Failed to delete contact"
                )
                _toastMessage.value = "Failed to delete contact"
            }
        }
    }
}
