package com.example.roadsos.models

data class ChatResponse(

    val reply: String,

    val intent_detected: String? = null,

    val priority: String? = null,

    val suggested_actions:
    List<SuggestedAction> = emptyList(),

    val source: String? = null
)