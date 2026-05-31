import urllib.request
import json
import sys

token = """eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg1NGFhNGMyM2VkZTdiOGNhODc1OWZiMDZlNmExZDU4OTI0MjVkMDYiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiS3VuYWxqaXQgS2FzaHlhcCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NLSVlRWjdjQ3h3ellTMWRHUVFaMExUZUZhQ29oRGVmaUxYdENDRUZiNlJicl94UERXND1zOTYtYyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9yb2Fkc29zLTcyMjY0IiwiYXVkIjoicm9hZHNvcy03MjI2NCIsImF1dGhfdGltZSI6MTc3OTg4MTg0NiwidXNlcl9pZCI6IlEwdVgwcVAxeWtZMlMyWGhjS1VueUlhV2g3bjIiLCJzdWIiOiJRMHVYMHFQMXlrWTJTMlhoY0tVbnlJYVdoN24yIiwiaWF0IjoxNzgwMjI4NzAyLCJleHAiOjE3ODAyMzIzMDIsImVtYWlsIjoia3VuYWxqaXRrQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTE2OTYwMzUyMjQ2NTI1ODg0NjE0Il0sImVtYWlsIjpbImt1bmFsaml0a0BnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.AUoV7GfGQyzzggPo4X0-ZdPuMdnl7St4Ch55DT8-oiQULdlGO5l93FbZj4uPxl1SX-9ypP8tqaDr-cnDi_FpYijtK3oda7J16OBEl6YyPAq-g3xgujrhipa_aagOw4iw6dEKT0ekXMj737QKyZx8o9ORJplLJHOKV5G_aH3LlZezQ0B_CUUOjt0AEAHefbIPfkvy1J4HAn2TGvX93Fpv-ioSIH20nNSRlBYGs_NFC5C4W5fHqSUBwSpMYDm4VIe_MQ1r0rN8OkvlODDDrgnFhvIvepbldxqSE8Ug6bdQbtVKHJg6LilL4ERi3ETAfTEDCcfENz_6eRrGzbOh6vZImA"""

data = {
  "session_id": "test_session_123",
  "user_message": "My car broke down. Is there a garage nearby?",
  "context": {
    "lat": 37.7749,
    "lng": -122.4194,
    "nearest_police_phone": "911",
    "nearest_ambulance_phone": "911",
    "nearest_hospital_phone": "911",
    "nearest_towing_phone": "555-1234",
    "is_sos_active": False,
    "nearby_places": [
      {
        "id": "place1",
        "category": "garage",
        "name": "Bob's Auto Repair",
        "phone": "555-9876",
        "latitude": 37.7750,
        "longitude": -122.4190,
        "rating": 4.5,
        "isOpenNow": True,
        "distanceMeters": 150.0,
        "estimatedEtaMinutes": 2
      }
    ]
  },
  "history": []
}

req = urllib.request.Request(
    "https://roadsos-backend-ufme.onrender.com/chat", 
    data=json.dumps(data).encode("utf-8"), 
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
)

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS")
    print(response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"ERROR: {e}")
