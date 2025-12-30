# Frontend Testing Guide

## 🧪 Manual Testing Checklist

### Prerequisites
- Backend server running at `http://localhost:8000`
- Test user created in database (e.g., `dr.santiago` / `password123`)
- Frontend running at `http://localhost:5173`

---

## Test 1: Authentication Flow ✅

### Steps:
1. Navigate to `http://localhost:5173`
2. Verify automatic redirect to `/login`
3. Enter invalid credentials
   - Expected: Error message displayed
4. Enter valid credentials (`dr.santiago` / `password123`)
   - Expected: Redirect to `/calendar`
   - Expected: Token stored in localStorage
5. Refresh the page
   - Expected: User remains logged in
   - Expected: No redirect to login
6. Click user avatar in top right
   - Expected: Dropdown menu appears with user info
7. Click "Cerrar Sesión"
   - Expected: Redirect to `/login`
   - Expected: Token removed from localStorage

**Status:** ✅ PASS / ❌ FAIL

---

## Test 2: Global Navigation Persistence ✅

### Steps:
1. Log in successfully
2. Navigate to Calendar (`/calendar`)
   - Expected: Global navigation visible
   - Expected: "Agenda" tab highlighted
3. Navigate to Medical Attention (`/medical`)
   - Expected: Global navigation still visible
   - Expected: "Atención Médica" tab highlighted
4. Navigate to Records (`/records`)
   - Expected: Global navigation still visible
   - Expected: "Expedientes" tab highlighted
5. Navigate to Billing (`/billing`)
   - Expected: Global navigation still visible
6. Navigate to Finances (`/finances`)
   - Expected: Global navigation still visible

**Status:** ✅ PASS / ❌ FAIL

---

## Test 3: Calendar Functionality ✅

### Steps:
1. Navigate to `/calendar`
2. Verify calendar displays current week
3. Click "Hoy" button
   - Expected: Calendar jumps to today
4. Change view to "Día"
   - Expected: Day view displays
5. Change view to "Mes"
   - Expected: Month view displays
6. Click "Agendar Cita" button
   - Expected: Appointment creation modal opens
7. Filter doctors using sidebar checkboxes
   - Expected: Appointments filter by selected doctors
8. Use search bar
   - Expected: Appointments filter by search query

**Status:** ✅ PASS / ❌ FAIL

---

## Test 4: Medical Attention Page ✅

### Steps:
1. Navigate to `/medical`
2. Verify page loads without duplicate header
3. Verify global navigation is visible
4. Verify patient sidebar is visible (desktop)
5. Verify Maya assistant panel is visible (desktop)
6. Click "Libre" mode button
   - Expected: Form switches to free mode
7. Click "Guiado" mode button
   - Expected: Form switches to guided mode
8. Fill out form fields
9. Click "Guardar" button
   - Expected: Form saves (mock or API)
10. Click "Finalizar" button
    - Expected: Form submits (mock or API)

**Status:** ✅ PASS / ❌ FAIL

---

## Test 5: Global State Sharing ✅

### Steps:
1. Navigate to `/calendar`
2. Click on an appointment in the calendar
   - Expected: Appointment details modal opens
3. Select a patient from the appointment
   - Expected: Patient data stored in GlobalContext
4. Navigate to `/medical`
   - Expected: Selected patient data appears in Medical Attention
   - Expected: Patient name displayed in header
5. Navigate back to `/calendar`
   - Expected: Previous selections cleared or maintained

**Status:** ⚠️ PARTIALLY IMPLEMENTED (needs Calendar integration)

---

## Test 6: HTTP Services & API Integration ✅

### Network Tab Tests:

#### Authentication:
1. Open browser DevTools → Network tab
2. Login with valid credentials
3. Verify POST request to `/auth/login`
   - Expected: Status 200
   - Expected: Response contains `access_token`, `user` data
4. Navigate to any page after login
5. Verify requests include `Authorization: Bearer <token>` header

#### Patient Service (when integrated):
1. Navigate to a page that fetches patients
2. Verify GET request to `/patients`
3. Verify Authorization header present
4. Create a new patient
5. Verify POST request to `/patients` with patient data

#### Appointment Service (when integrated):
1. Navigate to Calendar
2. Verify GET request to `/appointments`
3. Create a new appointment
4. Verify POST request to `/appointments`
5. Update an appointment
6. Verify PUT request to `/appointments/{id}`

**Status:** ⚠️ INFRASTRUCTURE READY (needs Calendar/Medical integration)

---

## Test 7: Error Handling ✅

### Steps:
1. Stop the backend server
2. Try to login
   - Expected: Network error displayed
3. Restart backend
4. Login successfully
5. Stop backend again
6. Try to fetch data (navigate to Calendar)
   - Expected: Error handling works
7. Restart backend
8. Make API request with invalid token
   - Expected: Automatic logout and redirect to login

**Status:** ✅ PASS / ❌ FAIL

---

## Test 8: Responsive Design ✅

### Desktop (1920x1080):
1. Test all pages
   - Expected: All sidebars visible
   - Expected: All panels visible
   - Expected: Proper spacing

### Tablet (768x1024):
1. Test all pages
   - Expected: Sidebars collapse to icons or hide
   - Expected: Main content adjusts
   - Expected: Navigation remains accessible

### Mobile (375x667):
1. Test all pages
   - Expected: Mobile menu appears
   - Expected: Single column layout
   - Expected: All functionality accessible

**Status:** ✅ PASS / ❌ FAIL

---

## Test 9: Security ✅

### JWT Token Management:
1. Open browser DevTools → Application → Local Storage
2. Login successfully
3. Verify `token` key exists with JWT value
4. Copy token value
5. Decode token at https://jwt.io
   - Expected: Contains `sub` (username) and `rol` (role)
6. Logout
   - Expected: `token` key removed from localStorage
7. Manually add an expired/invalid token to localStorage
8. Refresh page
   - Expected: Automatic logout and redirect to login

**Status:** ✅ PASS / ❌ FAIL

---

## Test 10: Protected Routes ✅

### Steps:
1. Logout completely
2. Manually navigate to `/calendar`
   - Expected: Redirect to `/login`
3. Manually navigate to `/medical`
   - Expected: Redirect to `/login`
4. Manually navigate to `/records`
   - Expected: Redirect to `/login`
5. Login successfully
6. Navigate to each protected route
   - Expected: Access granted

**Status:** ✅ PASS / ❌ FAIL

---

## 🐛 Known Issues & Limitations

### Current Implementation:
- ✅ Authentication fully functional
- ✅ Global navigation persistent
- ✅ Layout unified across all routes
- ✅ HTTP services infrastructure ready
- ⚠️ Calendar still uses mock data (needs migration to API)
- ⚠️ Medical forms need API integration
- ⚠️ Cross-module communication partially implemented

### Technical Debt:
- Some TypeScript errors in voice module (pre-existing)
- Voice features require `@google/genai` package
- Calendar components need refactoring to use appointmentService

---

## 📝 Test Results Summary

| Test Category | Status | Notes |
|--------------|--------|-------|
| Authentication | ✅ | Fully functional |
| Navigation | ✅ | Persistent across routes |
| Calendar | ⚠️ | Works with mock data |
| Medical | ✅ | Layout refactored |
| State Sharing | ⚠️ | Infrastructure ready |
| API Services | ⚠️ | Created but not integrated |
| Error Handling | ✅ | 401 handling works |
| Responsive | ✅ | Tailwind responsive classes |
| Security | ✅ | JWT properly managed |
| Protected Routes | ✅ | All routes protected |

---

## 🔄 Next Steps

1. **Integrate Calendar with appointmentService**
   - Replace `getAppointments()` from mockData with API call
   - Update `createAppointment()` to use API
   - Update `updateAppointment()` to use API

2. **Integrate Medical with patientService**
   - Fetch patient data from API
   - Save medical records to API
   - Load existing records from API

3. **Complete cross-module communication**
   - Calendar → Medical: Pass selected patient
   - Medical → Calendar: Reflect appointment updates

4. **Add loading states**
   - Show spinners during API calls
   - Disable buttons during submission
   - Add skeleton loaders

5. **Add toast notifications**
   - Success messages for saves
   - Error messages for failures
   - Info messages for warnings

---

## 💻 Developer Testing Commands

```bash
# Start dev server
cd Frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Check TypeScript
npx tsc --noEmit
```

---

## 🧰 Debugging Tips

### View Redux/Context State:
- Install React DevTools extension
- View GlobalContext state in Components tab

### Network Debugging:
- Open DevTools → Network tab
- Filter by "Fetch/XHR"
- Check request/response headers
- Verify Authorization header present

### Console Errors:
- Check browser console for errors
- Look for failed API calls
- Check for missing dependencies

### LocalStorage Inspection:
- DevTools → Application → Local Storage
- Check `token` and `user` keys
- Verify token is valid JWT

---

## 📞 Support

If tests fail, check:
1. Backend server is running
2. CORS is configured correctly
3. Test user exists in database
4. Environment variables are set correctly
5. All dependencies are installed (`npm install`)

For issues, provide:
- Test case that failed
- Error messages (console + network)
- Steps to reproduce
- Browser and version
