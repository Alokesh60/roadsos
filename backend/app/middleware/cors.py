from fastapi.middleware.cors import CORSMiddleware


# =====================================
# CORS CONFIGURATION
# =====================================
#
# PURPOSE:
# Restrict which frontends can access
# the backend API.
#
# WHY THIS MATTERS:
# Using:
#
# allow_origins=["*"]
# allow_credentials=True
#
# is insecure in production.
#
# It allows any website to send
# authenticated requests.
#
# =====================================


ALLOWED_ORIGINS = [

    # Android Emulator
    "http://10.0.2.2",

    # Local development
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",

    # Add your future frontend domains here
    # "https://roadsos.app",
]


def setup_cors(app):

    app.add_middleware(

        CORSMiddleware,

        allow_origins=ALLOWED_ORIGINS,

        allow_credentials=True,

        allow_methods=[

            "GET",
            "POST",
            "PUT",
            "DELETE"
        ],

        allow_headers=["*"],
    )