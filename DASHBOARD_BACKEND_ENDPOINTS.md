# Backend Endpoints Required for Dashboard

The dashboard is currently using mock data. The following endpoints need to be implemented in the backend for full functionality.

## Required Endpoints

### 1. GET `/stats/dashboard`

**Description:** Returns all main dashboard statistics.

**Authentication:** Required (JWT Bearer token)

**Response:**
```json
{
  "total_patients": 248,
  "active_patients": 186,
  "new_patients_this_month": 23,
  "total_appointments_today": 12,
  "total_appointments_week": 67,
  "total_appointments_month": 284,
  "appointments_by_status": {
    "pendiente": 45,
    "confirmada": 38,
    "completada": 156,
    "cancelada": 32,
    "no_asistio": 13
  },
  "revenue_today": 3250,
  "revenue_week": 18400,
  "revenue_month": 67500,
  "revenue_year": 780000,
  "top_treatments": [
    {
      "nombre": "Quiropedia Básica",
      "cantidad": 89
    },
    {
      "nombre": "Tratamiento de Uñas Encarnadas",
      "cantidad": 67
    }
  ],
  "ocupacion_porcentaje": 87,
  "upcoming_appointments": 156
}
```

**Database Queries Needed:**
- Count of total patients
- Count of active patients (recent appointments)
- Count of new patients this month
- Count of appointments by date ranges
- Count of appointments grouped by status
- Sum of revenue by date ranges
- Top treatments by count
- Calculation of calendar occupancy percentage

---

### 2. GET `/stats/appointments-trend?days=30`

**Description:** Returns appointment trends for the last N days.

**Authentication:** Required (JWT Bearer token)

**Query Parameters:**
- `days` (optional, default: 30): Number of days to retrieve

**Response:**
```json
[
  {
    "fecha": "2025-12-01",
    "cantidad": 12,
    "completadas": 10,
    "canceladas": 2
  },
  {
    "fecha": "2025-12-02",
    "cantidad": 15,
    "completadas": 13,
    "canceladas": 2
  }
]
```

**Database Queries Needed:**
- Group appointments by date for last N days
- Count total appointments per day
- Count completed appointments per day
- Count cancelled appointments per day

---

### 3. GET `/stats/revenue-trend`

**Description:** Returns monthly revenue trends for the current year.

**Authentication:** Required (JWT Bearer token)

**Response:**
```json
[
  {
    "mes": "Ene",
    "ingresos": 65000
  },
  {
    "mes": "Feb",
    "ingresos": 72000
  },
  {
    "mes": "Mar",
    "ingresos": 68000
  }
]
```

**Database Queries Needed:**
- Sum of revenue grouped by month for current year
- Join with payments/billing table

---

## Implementation Steps

1. **Create stats router** in backend:
   ```python
   from fastapi import APIRouter, Depends
   from auth import get_current_user, User
   
   router = APIRouter(prefix="/stats", tags=["Estadísticas"])
   ```

2. **Implement database queries** using existing database connection pool

3. **Add security** - all endpoints should require authentication

4. **Test endpoints** with Postman or curl

5. **Update frontend** - Once endpoints are ready, update `DashboardPage.tsx`:
   - Uncomment real API calls
   - Comment out mock data calls
   - Test error handling

## Database Tables Used

- `pacientes` - Patient information
- `citas` - Appointments
- `tratamientos` - Treatments
- `pagos` / `facturacion` - Revenue data (if exists)

## Performance Considerations

- Add database indexes on frequently queried fields:
  - `citas.fecha_hora_inicio`
  - `citas.estado`
  - `pacientes.fecha_registro`
  
- Consider caching dashboard stats (Redis) with 5-15 minute TTL

- Use database aggregation queries instead of loading all data to Python

## Testing

After implementing endpoints, test with:

```bash
# Get dashboard stats
curl -X GET "http://localhost:8000/stats/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get appointment trends
curl -X GET "http://localhost:8000/stats/appointments-trend?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get revenue trends
curl -X GET "http://localhost:8000/stats/revenue-trend" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
