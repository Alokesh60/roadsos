import json
from datetime import datetime

from app.db.sqlite_db import (
    get_connection
)


def save_emergency_log(

    message: str,

    detected_type: str,

    priority: str,

    confidence: float,

    country: str,

    classification_status: str,

    recommended_service: dict
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO emergency_logs (

        message,

        detected_type,

        priority,

        confidence,

        country,

        classification_status,

        recommended_service,

        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        message,

        detected_type,

        priority,

        confidence,

        country,

        classification_status,

        json.dumps(recommended_service),

        datetime.utcnow().isoformat()

    ))

    conn.commit()

    conn.close()