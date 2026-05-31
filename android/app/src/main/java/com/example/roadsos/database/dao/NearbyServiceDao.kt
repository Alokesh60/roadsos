package com.example.roadsos.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.roadsos.database.entity.LocalNearbyService
import kotlinx.coroutines.flow.Flow

@Dao
interface NearbyServiceDao {
    @Query("SELECT * FROM nearby_services")
    fun getAllServices(): Flow<List<LocalNearbyService>>

    @Query("SELECT * FROM nearby_services")
    fun getAllServicesSync(): List<LocalNearbyService>

    @Query("SELECT * FROM nearby_services WHERE category = :category ORDER BY distanceMeters ASC")
    fun getServicesByCategory(category: String): Flow<List<LocalNearbyService>>

    @Query("SELECT * FROM nearby_services WHERE category = :category ORDER BY distanceMeters ASC")
    fun getServicesByCategorySync(category: String): List<LocalNearbyService>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insertServices(services: List<LocalNearbyService>)

    @Query("DELETE FROM nearby_services WHERE category = :category")
    fun deleteByCategory(category: String)
}
