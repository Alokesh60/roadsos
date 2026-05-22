CREATE TABLE emergency_services (
    id BIGSERIAL PRIMARY KEY,

    name TEXT NOT NULL,

    type TEXT NOT NULL CHECK (
        type IN (
            'hospital',
            'trauma_center',
            'ambulance',
            'police_station',
            'towing_service',
            'puncture_shop',
            'blood_bank',
            'fire_station',
            'showroom'
        )
    ),

    phone TEXT,

    address TEXT,

    city TEXT,
    state TEXT,
    country TEXT,

    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,

    rating DOUBLE PRECISION DEFAULT 0,

    availability BOOLEAN DEFAULT true,

    verified BOOLEAN DEFAULT false,

    source TEXT,

    last_verified TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);