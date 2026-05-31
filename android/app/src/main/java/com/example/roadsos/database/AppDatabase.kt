package com.example.roadsos.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.roadsos.database.dao.EmergencyContactDao
import com.example.roadsos.database.dao.NearbyServiceDao
import com.example.roadsos.database.entity.LocalEmergencyContact
import com.example.roadsos.database.entity.LocalNearbyService

@Database(entities = [LocalEmergencyContact::class, LocalNearbyService::class], version = 3, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun emergencyContactDao(): EmergencyContactDao
    abstract fun nearbyServiceDao(): NearbyServiceDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "roadsos_local_db"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
