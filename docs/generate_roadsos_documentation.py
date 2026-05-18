from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
PDF_PATH = DOCS / "RoadSOS_Project_Documentation.pdf"


def font(size=22, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def round_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def create_visual_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)

    # Suggested UI section mockup: live incident command panel.
    w, h = 1400, 820
    img = Image.new("RGB", (w, h), "#08111f")
    d = ImageDraw.Draw(img)
    title = font(52, True)
    h1 = font(36, True)
    body = font(24)
    small = font(20)

    d.text((70, 55), "Suggested Home Upgrade: Live Emergency Command Panel", fill="#ffffff", font=title)
    d.text((72, 120), "A backend-driven first screen for active SOS state, ETA, contacts notified, and facility assignment.", fill="#aab4c3", font=body)

    round_rect(d, (70, 190, 590, 710), 34, "#121b2a", "#26364d", 3)
    round_rect(d, (105, 230, 555, 315), 28, "#7a0f0f")
    d.text((130, 247), "SOS ACTIVE", fill="#ffffff", font=h1)
    d.text((132, 292), "Incident ID: SOS-2026-00082", fill="#ffd5d5", font=small)

    round_rect(d, (105, 350, 555, 455), 24, "#182538")
    d.text((130, 370), "Ambulance A108 assigned", fill="#ffffff", font=body)
    d.text((130, 405), "ETA 3 min  |  AIIMS Trauma Centre", fill="#4dff88", font=small)

    round_rect(d, (105, 485, 555, 670), 24, "#101827")
    for idx, line in enumerate(["1. Location shared", "2. Contacts notified", "3. Hospital alerted", "4. Police optional"]):
        y = 515 + idx * 38
        d.ellipse((130, y + 4, 150, y + 24), fill="#d62828")
        d.text((170, y), line, fill="#d8e2f0", font=small)

    round_rect(d, (660, 190, 1330, 710), 34, "#101827", "#26364d", 3)
    d.text((700, 225), "Map + Service Assignment", fill="#ffffff", font=h1)
    for x in range(720, 1260, 110):
        d.line((x, 300, x, 650), fill="#263245", width=5)
    for y in range(320, 650, 80):
        d.line((700, y, 1280, y), fill="#263245", width=5)
    d.line((785, 595, 930, 490, 1090, 445, 1215, 350), fill="#d62828", width=14, joint="curve")
    d.ellipse((760, 572, 805, 617), fill="#4da3ff")
    d.ellipse((1190, 326, 1235, 371), fill="#d62828")
    round_rect(d, (885, 535, 1120, 595), 20, "#14253c")
    d.text((910, 550), "ETA 3 min", fill="#4dff88", font=body)
    img.save(ASSETS / "suggested_command_panel.png")

    # Backend integration architecture diagram.
    w, h = 1400, 720
    img = Image.new("RGB", (w, h), "#ffffff")
    d = ImageDraw.Draw(img)
    title = font(46, True)
    h1 = font(28, True)
    body = font(20)
    d.text((60, 40), "RoadSOS Backend Integration Flow", fill="#111827", font=title)
    boxes = [
        (70, 150, 330, 300, "Android Compose UI", "Screens emit events\nand render state"),
        (420, 150, 680, 300, "Repository Layer", "Retrofit/Ktor calls\nmaps DTOs to UI"),
        (770, 150, 1030, 300, "FastAPI Backend", "/login /nearby\n/search /chat /sos"),
        (1120, 150, 1380, 300, "Data + AI", "Supabase, maps,\nclassifier, chatbot"),
        (420, 420, 680, 570, "Error Mapper", "HTTP/network/domain\nerrors to UI state"),
        (770, 420, 1030, 570, "Realtime Updates", "Notifications,\nSOS status, ETA"),
    ]
    for x1, y1, x2, y2, heading, text in boxes:
        fill = "#fff5f5" if "Error" in heading else "#f8fafc"
        outline = "#d62828" if "Error" in heading else "#334155"
        round_rect(d, (x1, y1, x2, y2), 24, fill, outline, 3)
        d.text((x1 + 24, y1 + 24), heading, fill="#111827", font=h1)
        for idx, line in enumerate(text.split("\n")):
            d.text((x1 + 24, y1 + 72 + idx * 28), line, fill="#475569", font=body)
    arrows = [
        ((330, 225), (420, 225)),
        ((680, 225), (770, 225)),
        ((1030, 225), (1120, 225)),
        ((900, 300), (900, 420)),
        ((770, 495), (680, 495)),
        ((550, 420), (550, 300)),
    ]
    for start, end in arrows:
        d.line((start[0], start[1], end[0], end[1]), fill="#d62828", width=6)
        ex, ey = end
        sx, sy = start
        if ex > sx:
            poly = [(ex, ey), (ex - 18, ey - 10), (ex - 18, ey + 10)]
        elif ex < sx:
            poly = [(ex, ey), (ex + 18, ey - 10), (ex + 18, ey + 10)]
        elif ey > sy:
            poly = [(ex, ey), (ex - 10, ey - 18), (ex + 10, ey - 18)]
        else:
            poly = [(ex, ey), (ex - 10, ey + 18), (ex + 10, ey + 18)]
        d.polygon(poly, fill="#d62828")
    img.save(ASSETS / "backend_flow.png")


def styles():
    base = getSampleStyleSheet()
    base["Title"].fontName = "Helvetica-Bold"
    base["Title"].fontSize = 25
    base["Title"].leading = 31
    base["Title"].textColor = colors.HexColor("#111827")
    base["Heading1"].fontSize = 18
    base["Heading1"].leading = 23
    base["Heading1"].spaceBefore = 14
    base["Heading1"].spaceAfter = 8
    base["Heading1"].textColor = colors.HexColor("#991b1b")
    base["Heading2"].fontSize = 14
    base["Heading2"].leading = 18
    base["Heading2"].spaceBefore = 10
    base["Heading2"].spaceAfter = 6
    base["Heading2"].textColor = colors.HexColor("#1f2937")
    base["BodyText"].fontSize = 9.5
    base["BodyText"].leading = 13
    base["BodyText"].spaceAfter = 5
    base.add(ParagraphStyle(name="TableCell", parent=base["BodyText"], fontSize=7.2, leading=9.2, wordWrap="CJK", spaceAfter=0))
    base.add(ParagraphStyle(name="TableHeader", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.4, leading=9.4, textColor=colors.white, wordWrap="CJK", spaceAfter=0))
    base.add(ParagraphStyle(name="CenterSmall", parent=base["BodyText"], alignment=TA_CENTER, textColor=colors.HexColor("#64748b")))
    base.add(ParagraphStyle(name="Callout", parent=base["BodyText"], backColor=colors.HexColor("#fff5f5"), borderColor=colors.HexColor("#fecaca"), borderWidth=1, borderPadding=8, leading=14))
    return base


def p(text, style):
    return Paragraph(escape(text), style)


def bullet(text, style):
    return p(f"• {text}", style)


def table(data, widths=None):
    s = styles()
    wrapped = []
    for row_index, row in enumerate(data):
        wrapped_row = []
        for cell in row:
            if isinstance(cell, Paragraph):
                wrapped_row.append(cell)
            else:
                style = s["TableHeader"] if row_index == 0 else s["TableCell"]
                wrapped_row.append(Paragraph(escape(str(cell)), style))
        wrapped.append(wrapped_row)

    t = Table(wrapped, colWidths=widths, repeatRows=1, splitByRow=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("LEADING", (0, 0), (-1, -1), 9.2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.65 * inch, 0.42 * inch, "RoadSOS frontend/backend handoff documentation")
    canvas.drawRightString(A4[0] - 0.65 * inch, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    create_visual_assets()
    s = styles()
    story = []
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title="RoadSOS Project Documentation",
    )

    story.append(p("RoadSOS Complete Project Documentation", s["Title"]))
    story.append(p("Frontend progress, screen specifications, error handling, and backend integration handoff", s["Heading2"]))
    story.append(p(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')} from the local repository. Android source folder was not modified.", s["CenterSmall"]))
    story.append(Spacer(1, 12))
    story.append(RLImage(str(ASSETS / "backend_flow.png"), width=7.15 * inch, height=3.68 * inch))
    story.append(Spacer(1, 10))
    story.append(p("Executive Summary", s["Heading1"]))
    story.append(p("RoadSOS is a Kotlin + Jetpack Compose + Material 3 Android emergency assistance frontend. The current implementation is hackathon-ready and backend-ready: the UI flows, navigation, empty states, simulated errors, search/filter behavior, profile editing, permissions journey, and emergency/SOS surfaces are already implemented on the client side using local Compose state. Backend integration now needs to replace hardcoded data and simulated responses with authenticated API calls, persistent storage, live location, service discovery, AI chat, notifications, and SOS dispatch workflows.", s["BodyText"]))
    story.append(p("Important current-state note: the frontend currently stores login, contacts, services, profile, notifications, and AI chat in memory. That makes the UI demonstrable, but data resets when the process restarts. The backend should expose stable contracts and the Android side should introduce a repository/ViewModel layer before production.", s["Callout"]))

    story.append(p("Technology Stack", s["Heading1"]))
    story.append(table([
        ["Layer", "Current implementation", "Backend handoff meaning"],
        ["Android UI", "Kotlin, Jetpack Compose, Material 3", "Backend can focus on JSON contracts while Android binds responses into Compose state."],
        ["Architecture", "Composable screens, local remember/mutableStateOf, manual screen router", "Add ViewModels, repositories, DTOs, and sealed UI states without redesigning screens."],
        ["Theme", "Custom dark theme, red emergency accent, reusable colors", "Backend severity/status can map to existing red, green, gray, and alert surfaces."],
        ["Backend", "FastAPI skeleton with /login, /me, /nearby, /live-nearby, /search; API_CONTRACT.md describes /chat", "Connect Android to these routes and add missing routes for contacts, profile, notifications, SOS, OTP, and Google auth."],
    ], [1.25 * inch, 2.15 * inch, 3.45 * inch]))

    story.append(p("Project Folder Map", s["Heading1"]))
    story.append(table([
        ["Path", "Purpose"],
        ["android/app/src/main/java/com/example/roadsos/MainActivity.kt", "App entry point, splash/auth/permission/main flow routing."],
        ["android/app/src/main/java/com/example/roadsos/screens/navigation/MainContainerScreen.kt", "Main screen router and bottom-tab state holder."],
        ["android/app/src/main/java/com/example/roadsos/screens/home/HomeScreen.kt", "Dashboard, map mock, quick actions, SOS section, notifications, bottom navigation."],
        ["android/app/src/main/java/com/example/roadsos/screens/services", "Service list, filters, service detail view."],
        ["android/app/src/main/java/com/example/roadsos/screens/contacts", "Emergency contact list, add form, search, delete confirmation."],
        ["android/app/src/main/java/com/example/roadsos/screens/ai/AIAssistantScreen.kt", "Chat-style emergency assistant UI with simulated AI response/error."],
        ["android/app/src/main/java/com/example/roadsos/screens/profile/ProfileScreen.kt", "Editable profile fields, permissions shortcut, logout."],
        ["android/app/src/main/java/com/example/roadsos/screens/permissions/PermissionScreen.kt", "Permission awareness/selection UI."],
        ["android/app/src/main/java/com/example/roadsos/ui/components/ErrorComponents.kt", "Reusable ErrorBanner, NoInternetBanner, LoadingView, EmptyStateCard, RetryButton."],
        ["backend/app/api", "FastAPI route modules currently available for auth, nearby, search, health, download; chatbot route exists but is empty."],
        ["API_CONTRACT.md", "AI/backend contract for /chat classification, severity, facility ranking, and AI response."],
    ], [3.25 * inch, 3.6 * inch]))

    story.append(PageBreak())
    story.append(p("App Flow", s["Heading1"]))
    flow_items = [
        "Launch starts in MainActivity.kt and renders RoadSoSApp inside RoadSoSTheme.",
        "RoadSoSApp shows SplashScreen for 2.5 seconds using LaunchedEffect and delay.",
        "After splash, unauthenticated users see AuthScreen.",
        "Login success directly opens MainContainerScreen.",
        "Signup success opens PermissionScreen first; Save and Continue then opens MainContainerScreen.",
        "MainContainerScreen controls Home, Services, Service Detail, Contacts, Add Contact, AI, Profile, and Permissions.",
        "Android BackHandler returns most nested screens to their parent or to Home depending on the current route.",
    ]
    for item in flow_items:
        story.append(bullet(item, s["BodyText"]))

    story.append(p("Screen Specifications", s["Heading1"]))
    screens = [
        ("Splash Screen", "screens/splash/SplashScreen.kt", "Branding, launch transition, animated SOS pulse, background image, dark overlay, progress indicator.", "No backend dependency. Later can check persisted session/token while splash is visible.", "If session refresh fails, route to AuthScreen and show auth error there."),
        ("Authentication", "screens/auth/AuthScreen.kt", "Signup/login toggle, name field for signup, phone field, OTP field, send OTP label, Google continuation button, local loading/error variables.", "Implement send OTP, verify OTP, login, signup, Google sign-in, token persistence, refresh token. Replace direct success callbacks with API result handling.", "Show Invalid OTP, network failure, rate limit, account exists/not found, Google failure, server unavailable. Use loading spinner during network calls."),
        ("Permission Setup", "screens/permissions/PermissionScreen.kt", "Permission cards for location, phone calls, SMS, notifications; Save and Continue; back support.", "Android should request actual runtime permissions and optionally send permission status to backend for user capability tracking.", "If permission is denied, show a non-blocking warning and allow degraded app mode. For permanently denied permissions, deep-link to app settings."),
        ("Home Dashboard", "screens/home/HomeScreen.kt", "Top header, GPS active indicator, notification popup, map mock, quick actions, SOS explainer, nearby services, no-internet banner, bottom nav.", "Fetch current user/location, nearby top services, notifications, live SOS status, map ETA, connectivity state. Quick actions should call service category endpoints or native phone intents.", "No internet banner; SOS failure banner; notification fetch failure should be quiet with retry; location missing should show permission/location CTA."),
        ("Bottom Navigation + SOS", "screens/home/HomeScreen.kt", "Floating bottom nav with Home, Services, Contacts, AI and central SOS button. SOS confirmation dialog currently simulates failure.", "Create SOS incident endpoint. On confirm send current location, user id, contacts, severity, selected service category, battery/network status if available.", "Handle SOS pending, sent, assigned, failed, canceled, resolved. Backend must return incident_id and status. UI should never silently fail an SOS."),
        ("Services List", "screens/services/ServicesScreen.kt", "Search, category filter chips, hardcoded service list, cards with distance/ETA/rating/call, empty state.", "Connect to /nearby and /search. Support lat/lon/radius/type/query, distance sorting, availability, contact number, geolocation.", "Show LoadingView during fetch, EmptyStateCard for zero results, ErrorBanner + RetryButton for failed fetch. Cache last known results for offline display."),
        ("Service Detail", "screens/services/ServiceDetailScreen.kt", "Map-style header, back support, ETA chip, title/status, distance/ETA/rating, Directions/Call Now, location, facilities, emergency contact.", "Fetch service by id or pass full service object from list. Directions should open maps route. Call Now should dial backend-provided phone number.", "If service details fail, show cached basic details with retry. If phone unavailable, disable call and show explanation."),
        ("Contacts List", "screens/contacts/ContactsScreen.kt", "Search by name/relation/number, add contact CTA, contact cards, priority chip, call button, delete confirmation.", "Add CRUD endpoints for contacts. Persist contacts per authenticated user. Contact call button should use ACTION_DIAL with stored number.", "Create/update/delete failures need inline or banner errors. Duplicate numbers and invalid phone format should be validated server-side and client-side."),
        ("Add Contact", "screens/contacts/AddContactScreen.kt", "Name, phone, relation, priority dropdown, validation that blocks blank fields, back support.", "POST contact to backend, return server id. Priority values are Primary, Secondary, Medical, SOS.", "Show field-level validation for bad phone number, duplicate priority rules, backend failure, and loading state while saving."),
        ("AI Assistant", "screens/ai/AIAssistantScreen.kt", "Chat top bar, safety banner, LazyColumn messages, input bar with imePadding, dummy response, AI unavailable banner.", "Connect to /chat contract. Send message, lat, lon, optional incident_id/context. Render ai_response, severity_detected, nearby facilities, and suspicious/test status.", "Show AI unavailable, timeout, rate limit, unsafe content, no location, empty response. Keep user message visible even when backend fails."),
        ("Profile", "screens/profile/ProfileScreen.kt", "Profile icon, editable name/phone/email, permission settings link, save changes, logout.", "GET /me, PATCH /profile, logout/revoke token, persist profile locally. Current isEditing defaults true and Save locks fields.", "Validation for email/phone/name, save loading state, conflict errors, session expired leading to AuthScreen."),
    ]
    for name, file, ui, backend, errors in screens:
        story.append(p(name, s["Heading2"]))
        story.append(table([
            ["File", file],
            ["Current UI", ui],
            ["Backend work", backend],
            ["Error handling", errors],
        ], [1.35 * inch, 5.5 * inch]))

    story.append(PageBreak())
    story.append(p("Reusable UI Components", s["Heading1"]))
    story.append(table([
        ["Component", "File", "Purpose", "Backend use"],
        ["ErrorBanner(message)", "ui/components/ErrorComponents.kt", "Red warning card for failed operations.", "Use for API/network/domain errors that need user action."],
        ["NoInternetBanner()", "ui/components/ErrorComponents.kt", "Full-width connectivity warning.", "Bind to network monitor and offline repository state."],
        ["LoadingView()", "ui/components/ErrorComponents.kt", "Centered red Material spinner.", "Use while API calls are in progress."],
        ["EmptyStateCard(title, subtitle)", "ui/components/ErrorComponents.kt", "Reusable empty result card.", "Use for no services, no contacts, no notifications, no chat history."],
        ["RetryButton(onRetry)", "ui/components/ErrorComponents.kt", "Consistent retry action.", "Call repository fetch again after recoverable failures."],
        ["BottomNavBar / SOSNavButton", "screens/home/HomeScreen.kt", "Shared navigation and SOS confirmation entry point.", "Connect center SOS to incident creation and status polling."],
        ["AuthInputField / InputField / ProfileInputField", "auth, contacts, profile screens", "Consistent styled text inputs.", "Add validation states and field-level errors."],
    ], [1.45 * inch, 1.65 * inch, 1.85 * inch, 1.9 * inch]))

    story.append(p("Recommended Error Handling Architecture", s["Heading1"]))
    story.append(p("The backend should return predictable HTTP status codes and stable JSON error bodies. The Android side should translate them into a sealed UI error model rather than checking raw strings in each screen.", s["BodyText"]))
    story.append(table([
        ["Error category", "Backend response", "Android UI behavior"],
        ["Network offline", "No server response", "NoInternetBanner, keep cached data, disable high-risk actions except native emergency call."],
        ["Timeout", "Client timeout or 504", "ErrorBanner with RetryButton; keep user-entered form/chat text."],
        ["Unauthorized/session expired", "401", "Clear token, show AuthScreen, preserve non-sensitive local state when possible."],
        ["Permission missing", "403 or app-side permission state", "Show permission CTA and explain degraded mode."],
        ["Validation", "400/422 with field map", "Show field-level errors near input and block submit."],
        ["Not found", "404", "Service/contact unavailable state with back navigation."],
        ["Rate limited", "429", "Show cooldown message; disable button temporarily."],
        ["Server failure", "500/503", "ErrorBanner with support-safe wording; log request id if provided."],
        ["SOS dispatch failed", "409/500/503 with incident status", "Prominent banner/dialog; offer retry and direct emergency calling."],
        ["AI unavailable", "503 or AI timeout", "Keep chat message, show AI unavailable banner, optionally offer canned first-aid guidance."],
    ], [1.55 * inch, 2.05 * inch, 3.25 * inch]))

    story.append(p("Suggested API Contracts", s["Heading1"]))
    api_rows = [
        ["POST /auth/send-otp", "{ phone }", "Send OTP; return request_id, expires_at, retry_after."],
        ["POST /auth/verify-otp", "{ phone, otp, request_id }", "Verify login/signup; return user, access_token, refresh_token, is_new_user."],
        ["POST /auth/google", "{ id_token }", "Google auth; return same token payload."],
        ["GET /me", "Bearer token", "Return current profile; backend already has a basic route."],
        ["PATCH /profile", "{ name, phone, email }", "Update editable profile fields."],
        ["GET /nearby", "lat, lon, radius, type", "Return nearby services; backend route exists."],
        ["GET /search", "q", "Return services matching query; backend route exists."],
        ["GET /services/{id}", "service id", "Return detail page data: address, facilities, phone, open status, ETA metadata."],
        ["GET /contacts", "Bearer token", "Return user's emergency contacts."],
        ["POST /contacts", "{ name, relation, phone, priority }", "Create contact and return id."],
        ["DELETE /contacts/{id}", "contact id", "Delete after confirmation."],
        ["POST /sos", "{ lat, lon, message?, contacts, severity? }", "Create SOS incident; return incident_id, status, notified contacts, assigned service."],
        ["GET /sos/{incident_id}", "incident id", "Poll incident state: pending, dispatched, assigned, resolved, failed."],
        ["GET /notifications", "Bearer token", "Return emergency alerts and status updates."],
        ["POST /chat", "{ message, lat, lon, incident_id? }", "Use API_CONTRACT.md: return facilities, ai_response, severity_detected."],
    ]
    story.append(table([["Endpoint", "Request", "Frontend usage"]] + api_rows, [1.65 * inch, 2.1 * inch, 3.1 * inch]))

    story.append(PageBreak())
    story.append(p("Data Models Android Will Need", s["Heading1"]))
    story.append(table([
        ["Model", "Important fields"],
        ["User", "id, name, phone, email, avatar_url, created_at, permission_status."],
        ["EmergencyService", "id, name, type, distance_km, eta_minutes, rating, phone, address, lat, lon, open_now, facilities, availability_status."],
        ["EmergencyContact", "id, name, relation, phone, priority, verified, created_at."],
        ["Notification", "id, title, body, type, severity, created_at, read, incident_id."],
        ["SOSIncident", "id, user_id, lat, lon, status, assigned_service_id, eta_minutes, contacts_notified, created_at, resolved_at, failure_reason."],
        ["ChatMessage", "id, role(user/assistant/system), text, time, severity_detected, related_facilities, error_state."],
        ["ApiError", "code, message, field_errors, request_id, retry_after_seconds."],
    ], [1.85 * inch, 5.0 * inch]))

    story.append(p("Backend Integration Steps", s["Heading1"]))
    steps = [
        "Add Android networking dependencies such as Retrofit or Ktor, kotlinx.serialization/Moshi/Gson, and OkHttp logging for debug builds.",
        "Create DTOs matching backend responses and domain models matching UI needs.",
        "Introduce repositories: AuthRepository, ServiceRepository, ContactRepository, SOSRepository, ChatRepository, ProfileRepository, NotificationRepository.",
        "Move per-screen state from remember into ViewModels with sealed states: Loading, Success, Empty, Error.",
        "Persist access/refresh tokens in EncryptedSharedPreferences or DataStore.",
        "Add network connectivity monitoring and bind it to NoInternetBanner.",
        "Replace hardcoded lists in ServicesScreen, ContactsScreen, HomeScreen, NotificationPopup, and AIAssistantScreen.",
        "Add runtime permission requests using ActivityResultContracts for location/call/SMS/notification.",
        "Wire native intents: ACTION_DIAL for call buttons and maps intent for Directions.",
        "Add SOS status polling or realtime channel, because emergency dispatch should update without manual refresh.",
    ]
    for item in steps:
        story.append(bullet(item, s["BodyText"]))

    story.append(p("Current Gaps and Improvement Scope", s["Heading1"]))
    story.append(table([
        ["Area", "Current state", "Recommended improvement"],
        ["Navigation", "Manual enum router", "Use Navigation Compose for back stack, args, and deep links."],
        ["State", "remember state inside Composables", "Move business state to ViewModels and repositories."],
        ["Auth", "Direct callback success; no real OTP", "Implement real OTP/Google auth, token storage, session refresh."],
        ["Location", "Static text and mock map", "Use fused location provider and maps SDK or backend map tiles/ETA."],
        ["Services", "Hardcoded local list", "Fetch dynamic nearby/live services with cache and retry."],
        ["Contacts", "In-memory list", "Persist per user; sync with backend; support edit/reorder/verification."],
        ["SOS", "Confirmation then simulated failure", "Create incident lifecycle with retry, fallback call, notifications, and audit log."],
        ["AI", "Dummy response and error", "Connect to /chat, severity-aware UI, preserve history."],
        ["Notifications", "Static popup data", "Fetch/push notifications; mark read; link to incident/service detail."],
        ["Accessibility", "contentDescription mostly null", "Add meaningful descriptions for emergency controls."],
        ["Security", "No token/data storage yet", "Encrypt tokens, avoid logging sensitive emergency data."],
        ["Testing", "Default sample tests only", "Add ViewModel unit tests, API mapper tests, and Compose UI tests for critical flows."],
    ], [1.2 * inch, 2.15 * inch, 3.5 * inch]))

    story.append(p("Suggested UI Enhancements With Mockup", s["Heading1"]))
    story.append(RLImage(str(ASSETS / "suggested_command_panel.png"), width=7.15 * inch, height=4.18 * inch))
    story.append(Spacer(1, 8))
    story.append(p("Recommended additions: an active SOS command panel, incident timeline, assigned ambulance/hospital details, contact notification status, and backend-generated incident ID. This helps the user understand that the emergency request is actually moving through the system, and gives the backend a clear set of states to expose.", s["BodyText"]))
    ui_ideas = [
        "Add an Active Incident banner on Home when /sos/{id} is pending, assigned, or failed.",
        "Add a severity chip from /chat severity_detected or SOS triage: serious, minor, default.",
        "Add a compact notification inbox count and read/unread state from backend.",
        "Add service availability badges: Open, Busy, No beds, Offline, Verified.",
        "Add contact delivery states: SMS sent, call attempted, failed, acknowledged.",
        "Add safe fallback actions: Call 108, Call 100, Share location via SMS/WhatsApp when backend is unreachable.",
    ]
    for item in ui_ideas:
        story.append(bullet(item, s["BodyText"]))

    story.append(PageBreak())
    story.append(p("Screen-to-Backend Ownership Matrix", s["Heading1"]))
    story.append(table([
        ["Frontend screen/component", "Backend/API owner should provide", "Acceptance criteria"],
        ["AuthScreen", "OTP send/verify, Google auth, token refresh", "Invalid OTP, loading, success, and session expiry paths all testable."],
        ["PermissionScreen", "Optional permission-status save endpoint", "Backend knows whether location/SMS/call capabilities are available."],
        ["HomeScreen TopSection", "User profile, GPS/location status, notification count", "Header shows real user/location state."],
        ["NotificationPopup", "GET /notifications and optional mark-read", "Alerts are dynamic, sorted newest first, and connected to incident/service detail."],
        ["LocationMapCard", "ETA, current location, assigned destination", "Map card can show real coordinates and current route summary."],
        ["QuickActionsSection", "Category service lookup and emergency phone numbers", "Ambulance/Police/Hospital/Towing cards open relevant action/data."],
        ["BottomNavBar SOS", "POST /sos and GET /sos/{id}", "SOS creates incident, returns id, and updates through lifecycle."],
        ["ServicesScreen", "GET /nearby, GET /search", "Filter/search results come from backend and handle empty/error/loading states."],
        ["ServiceDetailScreen", "GET /services/{id}", "Directions/call/location/facilities use real data."],
        ["ContactsScreen", "Contacts CRUD", "Contacts persist across app restarts and devices."],
        ["AIAssistantScreen", "POST /chat", "AI reply, severity, and ranked facilities render from backend response."],
        ["ProfileScreen", "GET /me, PATCH /profile, logout", "Profile is editable, persisted, and validated."],
    ], [1.8 * inch, 2.55 * inch, 2.5 * inch]))

    story.append(p("Implementation Notes for Backend Developer", s["Heading1"]))
    notes = [
        "Keep response shapes stable and include a top-level success boolean only if it is used consistently. Prefer proper HTTP codes plus a structured error body.",
        "Every protected route should require the same Bearer token verification used by /me and /nearby.",
        "Include request_id in error responses so Android can show/log support-safe diagnostics without exposing internals.",
        "For /nearby, return numeric distance_km and eta_minutes separately; Android can format them as '0.8 km' and '4 min'.",
        "For /chat, follow API_CONTRACT.md and include severity_detected so Android can highlight serious emergencies.",
        "For SOS, design idempotency. If the user taps Send SOS twice during a bad connection, the backend should not create duplicate incidents.",
        "For contacts and profile, validate phone numbers in E.164 where possible, but allow local emergency numbers such as 100 and 108.",
        "Avoid sending sensitive personal data in AI prompts unless required; send only emergency context, location, and nearby services needed for guidance.",
    ]
    for item in notes:
        story.append(bullet(item, s["BodyText"]))

    story.append(p("Final Handoff Summary", s["Heading1"]))
    story.append(p("The frontend has completed the core emergency UX: splash/auth flow, signup permissions, dashboard, simulated map, quick actions, SOS confirmation, bottom navigation, services list and detail, contact management, AI chat, profile editing, reusable error/empty/loading components, and dark emergency-first visual system. The next major milestone is backend binding: replace local state with API-backed ViewModels, introduce persistence and permissions, then harden SOS as the highest-priority workflow.", s["Callout"]))

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)


if __name__ == "__main__":
    build_pdf()
    print(PDF_PATH)
