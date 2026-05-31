package com.example.roadsos.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.roadsos.database.entity.LocalEmergencyContact

@Dao
interface EmergencyContactDao {
    @Query("SELECT * FROM emergency_contacts ORDER BY priority ASC")
    fun getAllContacts(): List<LocalEmergencyContact>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insertContacts(contacts: List<LocalEmergencyContact>)

    @Query("DELETE FROM emergency_contacts")
    fun clearAll()
}
