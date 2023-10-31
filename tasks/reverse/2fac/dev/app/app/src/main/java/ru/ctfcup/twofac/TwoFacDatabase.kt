package ru.ctfcup.twofac

import android.content.Context
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Room
import androidx.room.RoomDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Entity
data class TwoFacSecret(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val username: String,
    val domain: String,
    val secret: String
)

@Dao
interface TwoFacSecretDao {
    @Query("SELECT * FROM TwoFacSecret")
    suspend fun getAllTwoFactorSecrets(): List<TwoFacSecret>

    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertTwoFactorSecret(secret: TwoFacSecret)
}

@Database(entities = [TwoFacSecret::class], version = 2)
abstract class TwoFacDatabase : RoomDatabase() {
    abstract fun twoFactorSecretDao(): TwoFacSecretDao
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Singleton
    @Provides
    fun provideDatabase(@ApplicationContext context: Context): TwoFacDatabase =
        Room.databaseBuilder(context, TwoFacDatabase::class.java, "db").build()

    @Singleton
    @Provides
    fun provideSecretDao(db: TwoFacDatabase): TwoFacSecretDao = db.twoFactorSecretDao()
}

