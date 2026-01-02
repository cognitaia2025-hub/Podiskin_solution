# Staff Management Module - Quick Start Guide

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
python main.py
```
Backend should be running on `http://localhost:8000`

### 2. Start the Frontend
```bash
cd Frontend
npm run dev
```
Frontend should be running on `http://localhost:5173`

### 3. Access Staff Management
1. Login as Admin user
2. Navigate to: `http://localhost:5173/admin/staff`

---

## 📋 Testing the Backend

### Option 1: Automated Test Script
```bash
python test_staff_endpoints.py
```

This will test all endpoints:
- Login as admin
- List all users
- Create test user
- Update user
- Get user by ID
- Delete (deactivate) user
- List roles

### Option 2: Manual cURL Tests

**1. Login and get token:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Save the `access_token` from the response.

**2. List all users:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/users
```

**3. Create a new user:**
```bash
curl -X POST http://localhost:8000/auth/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_usuario": "recepcion.maria",
    "password": "temporal123",
    "nombre_completo": "María García",
    "email": "maria@podoskin.com",
    "id_rol": 3
  }'
```

**4. Update a user:**
```bash
curl -X PUT http://localhost:8000/auth/users/5 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_rol": 2}'
```

**5. Deactivate a user:**
```bash
curl -X DELETE http://localhost:8000/auth/users/5 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**6. List roles:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/roles
```

---

## 🎨 Frontend Usage

### Creating a New Staff Member
1. Click "Nuevo Miembro" button
2. Fill in the form:
   - Nombre Completo (required)
   - Email (required)
   - Nombre de Usuario (required, unique)
   - Contraseña Temporal (required, min 8 chars)
   - Rol (required, select from dropdown)
3. Click "Crear"
4. Toast notification will confirm success

### Editing a Staff Member
1. Click the edit icon (pencil) on any user row
2. Update desired fields:
   - Nombre Completo
   - Email
   - Rol
3. Click "Actualizar"
4. Toast notification will confirm success

**Note:** Username and password cannot be changed after creation.

### Deactivating a Staff Member
1. Click the delete icon (trash) on any user row
2. Confirm the action
3. User will be marked as inactive (soft delete)
4. Toggle "Mostrar inactivos" to see deactivated users

**Note:** You cannot deactivate yourself.

### Searching
- Type in the search bar to filter by:
  - Name
  - Email
  - Username
- Results update in real-time

---

## 🔐 Role IDs Reference

Use these IDs when creating/updating users:

| ID | Role | Description |
|----|------|-------------|
| 1 | Admin | Full system access |
| 2 | Podologo | Podiatrist - medical access |
| 3 | Recepcionista | Receptionist - scheduling & billing |
| 4 | Asistente | Assistant - limited read access |

---

## 🐛 Troubleshooting

### Backend errors

**"Only administrators can list users" (403)**
- You're not logged in as an admin
- Check your JWT token is valid
- Login with an admin account

**"Usuario no encontrado" (404)**
- The user ID doesn't exist
- Verify the ID with GET /auth/users

**"Error al crear usuario" (400)**
- Username or email already exists
- Check for duplicates

### Frontend errors

**"Error al cargar datos"**
- Backend is not running
- Check `http://localhost:8000` is accessible
- Check browser console for details

**Modal doesn't open**
- Check browser console for errors
- Verify you're logged in as admin
- Try refreshing the page

**Toast notifications not appearing**
- Check `react-toastify` is properly configured
- Verify `<ToastContainer />` is in `main.tsx`

---

## 📝 Default Test Users

If you ran the database initialization, you should have these users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| dr.santiago | password123 | Podologo |

Create more users via the Staff Management UI!

---

## 🛠️ Development Notes

### Backend Structure
```
backend/
├── auth/
│   ├── router.py      # User management endpoints added here
│   ├── database.py    # Database functions added here
│   ├── models.py      # Pydantic models
│   └── jwt_handler.py # Password hashing utilities
└── main.py           # FastAPI app (already includes auth router)
```

### Frontend Structure
```
Frontend/src/
├── services/
│   └── staffService.ts    # API client for user management
├── pages/
│   └── StaffManagement.tsx # Main UI component
└── App.tsx                # Routing (staff route added)
```

### Key Features
- ✅ No mock data - all real API calls
- ✅ Error handling with toast notifications
- ✅ Admin-only access control
- ✅ Soft delete (data preservation)
- ✅ Password hashing with bcrypt
- ✅ JWT authentication
- ✅ Responsive design
- ✅ Real-time search

---

## 🚨 Important Security Notes

1. **Passwords**: All passwords are hashed with bcrypt before storage
2. **Admin Only**: All endpoints require admin authentication
3. **Soft Delete**: Users are deactivated, not deleted from database
4. **Self-Protection**: Admins cannot deactivate themselves
5. **JWT Tokens**: All requests require valid JWT token in header

---

## 📞 Support

If you encounter issues:
1. Check the implementation summary: `STAFF_MANAGEMENT_IMPLEMENTATION.md`
2. Run the test script: `python test_staff_endpoints.py`
3. Check browser console and network tab
4. Check backend logs for errors

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can login as admin
- [ ] Can access `/admin/staff` route
- [ ] Staff list loads
- [ ] Can create new user
- [ ] Can edit user
- [ ] Can deactivate user
- [ ] Toast notifications appear
- [ ] Search works
- [ ] Role filtering works

**If all checkboxes pass, the module is working correctly!** 🎉
