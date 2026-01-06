# Podoskin Solution - Frontend

Sistema de gestión clínica para podología con autenticación, gestión de citas, expedientes médicos y asistente de voz IA.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend server running on port 8000

### Installation

1. **Install dependencies**
```bash
cd Frontend
npm install
```

2. **Configure environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

3. **Start development server**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🔐 Authentication

The application now includes a complete authentication system:

### Login Flow
1. Navigate to `/login`
2. Enter credentials:
   - Username: `dr.santiago` (or your test user)
   - Password: `password123`
3. Upon successful login, you'll be redirected to `/calendar`
4. JWT token is stored in localStorage and automatically included in all API requests

### Protected Routes
All routes except `/login` are protected and require authentication:
- `/calendar` - Calendar view
- `/medical` - Medical attention
- `/records` - Patient records
- `/billing` - Billing
- `/finances` - Finances

### Logout
Click on your profile picture in the top right corner and select "Cerrar Sesión"

## 🏗️ Architecture

### Directory Structure
```
Frontend/src/
├── auth/                    # Authentication system
│   ├── AuthContext.tsx      # Authentication context provider
│   ├── ProtectedRoute.tsx   # Route protection HOC
│   ├── LoginPage.tsx        # Login page component
│   └── authService.ts       # Auth HTTP service
├── context/                 # Global state management
│   ├── GlobalContext.tsx    # Global application context
│   ├── types.ts             # Context type definitions
│   └── MedicalFormContext.tsx  # Medical form context
├── services/                # HTTP Services
│   ├── api.ts               # Base Axios client with JWT interceptors
│   ├── patientService.ts    # Patient CRUD operations
│   ├── appointmentService.ts # Appointment CRUD operations
│   └── treatmentService.ts  # Medical treatments and diagnostics
├── layouts/                 # Layout components
│   └── AppLayout.tsx        # Unified global layout
├── components/              # Reusable components
│   ├── medical/             # Medical attention components
│   ├── Layout.tsx           # Calendar layout
│   ├── GlobalNavigation.tsx # Global navigation menu
│   └── ...
├── pages/                   # Page components
│   └── MedicalAttention.tsx # Medical attention page (refactored)
└── types/                   # TypeScript type definitions
```

## 🔄 State Management

### Global Context
The `GlobalContext` provides shared state across the entire application:

```typescript
import { useGlobalContext } from './context/GlobalContext';

const MyComponent = () => {
  const { 
    selectedPatient,      // Currently selected patient
    selectedAppointment,  // Currently selected appointment
    setSelectedPatient,   // Function to set patient
    setSelectedAppointment, // Function to set appointment
    clearSelections,      // Clear all selections
  } = useGlobalContext();
  
  // Use the shared state...
};
```

### Cross-Module Communication
Example: Selecting a patient in Calendar and viewing in Medical Attention

```typescript
// In Calendar component
const handlePatientClick = (patient: Patient) => {
  setSelectedPatient(patient);
  navigate('/medical');
};

// In Medical Attention component
const { selectedPatient } = useGlobalContext();
// selectedPatient is automatically available!
```

## 🌐 HTTP Services

### Making API Calls

All services use the base `api` client which automatically includes JWT tokens:

```typescript
import { getPatients, createPatient } from './services/patientService';
import { getAppointments, createAppointment } from './services/appointmentService';

// Fetch patients
const patients = await getPatients(page, perPage);

// Create new patient
const newPatient = await createPatient({
  name: 'Juan Pérez',
  phone: '555-1234',
  email: 'juan@example.com'
});

// Fetch appointments
const appointments = await getAppointments({
  start_date: '2024-01-01',
  end_date: '2024-01-31',
  doctor_id: '1'
});
```

### Error Handling

The `api` client automatically handles authentication errors:
- **401 Unauthorized**: Automatically logs out and redirects to login
- **Other errors**: Thrown as exceptions for component-level handling

## 🎨 UI Components

### Navigation
- **Global Navigation**: Persistent across all routes (Calendar, Medical, Records, Billing, Finances)
- **User Menu**: Profile picture with dropdown showing name, role, and logout option

### Layouts
- **AppLayout**: Unified layout wrapping all authenticated routes
- **Layout**: Specialized layout for Calendar views with sidebar

## 🔧 Development

### Building
```bash
npm run build
```

### Linting
```bash
npm run lint
```

### Preview Production Build
```bash
npm run preview
```

## 📝 Important Notes

### Mock Data vs Real API
Currently, the Calendar still uses mock data from `services/mockData.ts`. The infrastructure is ready:
- ✅ Authentication system functional
- ✅ HTTP service layer created
- ✅ Global state management in place
- ⚠️ Calendar components need migration from mock data to real API calls

### Medical Attention Module
- Header and TopNavigation removed to use global navigation
- Now reads `selectedPatient` from GlobalContext
- Falls back to mock data if no patient is selected
- Compact header with patient name and action buttons

### Environment Variables
Never commit `.env` files. Use `.env.example` as a template.

## 🔐 Security

### JWT Tokens
- Stored in localStorage (key: `token`)
- Automatically included in all API requests via Axios interceptor
- Cleared on logout or 401 errors

### Protected Routes
All routes except `/login` require authentication. Unauthenticated users are redirected to login page.

## 📚 Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **date-fns** - Date utilities

## 🤝 Contributing

When making changes:
1. Always use TypeScript
2. Follow existing code patterns
3. Update this README if adding new features
4. Test authentication flows thoroughly
5. Ensure all API calls go through the `api` client

---

## Original Vite Template Info

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

