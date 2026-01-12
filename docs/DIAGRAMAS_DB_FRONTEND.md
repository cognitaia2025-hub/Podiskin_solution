# 📊 DIAGRAMAS: BASE DE DATOS ↔ FRONTEND

## 🗺️ Diagrama 1: Arquitectura General del Sistema

```mermaid
graph TB
    subgraph Frontend["🖥️ FRONTEND (React + TypeScript)"]
        Calendar[📅 Calendar]
        Medical[🩺 Medical Attention]
        Records[📋 Medical Records]
        Patients[👥 Patients]
        Dashboard[📊 Dashboard]
        Billing[💰 Billing]
        Finances[💵 Finances]
        Admin[⚙️ Admin]
    end
    
    subgraph Backend["⚙️ BACKEND (FastAPI)"]
        CitasAPI[/api/citas]
        PacientesAPI[/api/pacientes]
        TratamientosAPI[/api/tratamientos]
        PagosAPI[/api/pagos]
        FacturasAPI[/api/facturas]
        StatsAPI[/api/stats]
        InventoryAPI[/api/inventario]
    end
    
    subgraph Database["🗄️ POSTGRESQL"]
        Citas[(citas)]
        Pacientes[(pacientes)]
        Usuarios[(usuarios)]
        Tratamientos[(tratamientos)]
        Pagos[(pagos)]
        Facturas[(facturas)]
        Inventario[(inventario)]
    end
    
    Calendar --> CitasAPI
    Medical --> CitasAPI
    Medical --> TratamientosAPI
    Patients --> PacientesAPI
    Billing --> PagosAPI
    Billing --> FacturasAPI
    Dashboard --> StatsAPI
    Admin --> InventoryAPI
    
    CitasAPI --> Citas
    PacientesAPI --> Pacientes
    TratamientosAPI --> Tratamientos
    PagosAPI --> Pagos
    FacturasAPI --> Facturas
    StatsAPI --> Citas
    StatsAPI --> Pagos
    InventoryAPI --> Inventario
    
    Citas -.FK.-> Pacientes
    Citas -.FK.-> Usuarios
    Pagos -.FK.-> Citas
    Facturas -.FK.-> Pagos
    
    style Frontend fill:#e3f2fd
    style Backend fill:#fff3e0
    style Database fill:#f3e5f5
```

---

## 📋 Diagrama 2: Modelo de Entidad-Relación (ER) - Tablas Principales

```mermaid
erDiagram
    USUARIOS ||--o{ CITAS : "atiende (id_podologo)"
    PACIENTES ||--o{ CITAS : "tiene (id_paciente)"
    PACIENTES ||--o{ ALERGIAS : "tiene"
    PACIENTES ||--o{ SIGNOS_VITALES : "registra"
    PACIENTES ||--o{ ANTECEDENTES_MEDICOS : "tiene"
    
    CITAS ||--o{ NOTA_CLINICA : "genera"
    CITAS ||--o{ DETALLE_CITA : "contiene"
    CITAS ||--|| PAGOS : "requiere"
    
    TRATAMIENTOS ||--o{ DETALLE_CITA : "incluye"
    
    PAGOS ||--|| FACTURAS : "genera"
    
    DETALLE_CITA ||--o{ MATERIALES_USADOS : "consume"
    INVENTARIO ||--o{ MATERIALES_USADOS : "provee"
    
    USUARIOS ||--o{ PODOLOGO_PACIENTE_ASIGNACION : "asigna"
    PACIENTES ||--o{ PODOLOGO_PACIENTE_ASIGNACION : "asignado_a"
    
    USUARIOS {
        int id PK
        string nombre_usuario UK
        string email UK
        string rol "Admin|Podologo|Recepcionista"
        boolean activo
    }
    
    PACIENTES {
        int id PK
        string primer_nombre
        string primer_apellido
        date fecha_nacimiento
        string telefono_principal
        string email
        int creado_por FK
    }
    
    CITAS {
        int id PK
        int id_paciente FK
        int id_podologo FK
        timestamp fecha_hora_inicio
        timestamp fecha_hora_fin
        string estado "Pendiente|Confirmada|En_Curso|Completada|Cancelada"
        boolean es_primera_vez
        string tipo_cita
        text notas_recepcion
    }
    
    NOTA_CLINICA {
        int id PK
        int id_cita FK
        int id_paciente FK
        text motivo_consulta
        text diagnostico_presuntivo
        text diagnostico_definitivo
        text plan_tratamiento
        int elaborado_por FK
    }
    
    DETALLE_CITA {
        int id PK
        int id_cita FK
        int id_tratamiento FK
        decimal precio_aplicado
        decimal descuento_porcentaje
        decimal precio_final
    }
    
    TRATAMIENTOS {
        int id PK
        string codigo_servicio UK
        string nombre_servicio
        decimal precio_base
        int duracion_minutos
        boolean activo
    }
    
    PAGOS {
        int id PK
        int id_cita FK
        decimal monto_total
        decimal monto_pagado
        string metodo_pago "Efectivo|Tarjeta|Transferencia"
        string estado_pago "Pagado|Parcial|Pendiente"
    }
    
    FACTURAS {
        int id PK
        int id_pago FK
        int id_paciente FK
        string rfc_receptor
        decimal subtotal
        decimal iva
        decimal total
        string uuid_sat "UUID del SAT"
        string estado "Timbrada|Cancelada"
    }
    
    INVENTARIO {
        int id PK
        string codigo_material UK
        string nombre_material
        int stock_actual
        int stock_minimo
        decimal costo_unitario
    }
    
    MATERIALES_USADOS {
        int id PK
        int id_detalle_cita FK
        int id_material FK
        int cantidad_usada
        decimal costo_unitario
    }
    
    ALERGIAS {
        int id PK
        int id_paciente FK
        string alergia
        string severidad "Leve|Moderada|Severa"
        boolean activo
    }
    
    SIGNOS_VITALES {
        int id PK
        int id_paciente FK
        decimal presion_arterial_sistolica
        decimal presion_arterial_diastolica
        decimal frecuencia_cardiaca
        decimal temperatura
        decimal peso
        decimal talla
        int registrado_por FK
    }
    
    PODOLOGO_PACIENTE_ASIGNACION {
        int id PK
        int podologo_id FK
        int paciente_id FK
        boolean es_podologo_principal
        timestamp fecha_asignacion
    }
```

---

## 🔄 Diagrama 3: FLUJO 1 - Cita → Expediente Médico (Auto-carga)

```mermaid
sequenceDiagram
    participant User as 👨‍⚕️ Podólogo
    participant Calendar as 📅 /calendar
    participant Medical as 🩺 /medical/attention
    participant Backend as ⚙️ API Backend
    participant DB as 🗄️ PostgreSQL
    
    User->>Calendar: Click en Cita #1234
    Calendar->>Medical: Navigate to /medical/attention?appointmentId=1234
    
    Medical->>Backend: GET /api/citas/1234
    
    Backend->>DB: SELECT * FROM citas WHERE id = 1234
    DB-->>Backend: {id_paciente: 567, id_podologo: 89, ...}
    
    Backend->>DB: SELECT * FROM pacientes WHERE id = 567
    DB-->>Backend: {nombre, fecha_nacimiento, ...}
    
    Backend->>DB: SELECT * FROM signos_vitales WHERE id_paciente = 567
    DB-->>Backend: [{presion_arterial, peso, ...}]
    
    Backend->>DB: SELECT * FROM alergias WHERE id_paciente = 567
    DB-->>Backend: [{alergia: "Penicilina", severidad: "Severa"}]
    
    Backend->>DB: SELECT * FROM antecedentes_medicos WHERE id_paciente = 567
    DB-->>Backend: [{condicion, fecha_diagnostico, ...}]
    
    Backend->>DB: SELECT * FROM nota_clinica WHERE id_paciente = 567 ORDER BY fecha DESC LIMIT 5
    DB-->>Backend: [{diagnostico, plan_tratamiento, ...}]
    
    Backend-->>Medical: JSON con cita + paciente + historial completo
    
    Medical->>Medical: setPatientData(response.paciente)
    Medical->>Medical: setVitalSigns(response.signos_vitales)
    Medical->>Medical: setAllergies(response.alergias)
    
    rect rgb(255, 200, 200)
        Note over Medical: ⚠️ ALERTA: Paciente alérgico a Penicilina
    end
    
    Medical->>User: Muestra expediente completo con alertas
    
    User->>Medical: Completa atención médica
    Medical->>Backend: POST /api/nota_clinica
    Backend->>DB: INSERT INTO nota_clinica (id_cita, id_paciente, diagnostico, ...)
    DB-->>Backend: nota_clinica.id = 5678
    
    Backend->>DB: UPDATE citas SET estado = 'Completada' WHERE id = 1234
    DB-->>Backend: OK
    
    Backend-->>Medical: ✅ Atención registrada exitosamente
```

---

## 🔄 Diagrama 4: FLUJO 2 - Paciente → Podólogo Asignado

```mermaid
graph TB
    subgraph Patients["👥 /patients"]
        SearchPatient[Buscar Paciente 567]
        PatientCard[Card del Paciente]
        AssignButton[Botón: Asignar Podólogo]
    end
    
    subgraph Database["🗄️ Base de Datos"]
        PacientesTable[(pacientes)]
        UsuariosTable[(usuarios)]
        AsignacionTable[(podologo_paciente_asignacion)]
    end
    
    subgraph Calendar["📅 /calendar"]
        CreateAppointment[Crear Nueva Cita]
        SuggestPodologo[Auto-sugiere Podólogo]
        FilterByDoctor[Filtro por Podólogo]
    end
    
    subgraph Dashboard["📊 /dashboard"]
        StatsByDoctor[Estadísticas por Podólogo]
        PatientCount[Pacientes por Podólogo]
    end
    
    SearchPatient -->|GET /api/pacientes/567| PacientesTable
    PacientesTable -->|JOIN| AsignacionTable
    AsignacionTable -->|JOIN| UsuariosTable
    UsuariosTable -->|Response| PatientCard
    
    PatientCard -->|"Podólogo: Dr. Santiago ✅"| PatientCard
    
    AssignButton -->|POST /api/asignaciones| AsignacionTable
    AsignacionTable -.->|"Notifica cambio"| CreateAppointment
    
    CreateAppointment -->|"Query asignación"| AsignacionTable
    AsignacionTable -->|"Sugiere: Dr. Santiago"| SuggestPodologo
    
    FilterByDoctor -->|"WHERE id_podologo = 89"| PacientesTable
    
    AsignacionTable -->|"GROUP BY podologo_id"| StatsByDoctor
    AsignacionTable -->|"COUNT(*)"| PatientCount
    
    style PatientCard fill:#c8e6c9
    style SuggestPodologo fill:#fff9c4
    style StatsByDoctor fill:#e1bee7
```

---

## 🔄 Diagrama 5: FLUJO 3 - Cita → Pago → Factura (Completo)

```mermaid
sequenceDiagram
    participant User as 👨‍⚕️ Podólogo
    participant Medical as 🩺 Medical Attention
    participant Billing as 💰 Billing
    participant Backend as ⚙️ API Backend
    participant DB as 🗄️ PostgreSQL
    participant SAT as 🏛️ SAT (Facturación)
    
    User->>Medical: Finalizar atención de Cita #1234
    Medical->>Backend: POST /api/citas/1234/complete
    
    Backend->>DB: UPDATE citas SET estado = 'Completada'
    
    Backend->>DB: INSERT INTO detalle_cita (id_cita, id_tratamiento, precio)
    Note over DB: Tratamiento 1: Quiropodia $500 (10% desc) = $450
    Note over DB: Tratamiento 2: Uñero $300 = $300
    
    Backend-->>Medical: ✅ Cita completada
    Medical->>User: Redirect to /billing?appointmentId=1234
    
    User->>Billing: Vista de facturación
    Billing->>Backend: GET /api/citas/1234/detalle
    Backend->>DB: SELECT * FROM detalle_cita WHERE id_cita = 1234
    DB-->>Backend: [{tratamiento_1: $450}, {tratamiento_2: $300}]
    Backend-->>Billing: Total a cobrar: $750.00 MXN
    
    Billing->>User: Muestra resumen de tratamientos
    User->>Billing: Click "Registrar Pago"
    
    Billing->>Backend: POST /api/pagos {id_cita: 1234, monto: 750, metodo: "Tarjeta"}
    Backend->>DB: INSERT INTO pagos (id_cita, monto_total, metodo_pago, estado_pago)
    DB-->>Backend: pagos.id = 9876
    
    User->>Billing: ¿Requiere factura? (RFC del paciente)
    Billing->>Backend: POST /api/facturas {id_pago: 9876, rfc: "XAXX010101000"}
    
    Backend->>DB: INSERT INTO facturas (id_pago, rfc_receptor, subtotal, iva, total)
    Note over DB: Subtotal: $750.00<br/>IVA (16%): $120.00<br/>Total: $870.00
    
    Backend->>SAT: Timbrar CFDI (API PAC)
    
    alt Timbrado Exitoso
        SAT-->>Backend: UUID: 12345-ABCD-EFGH, XML firmado
        Backend->>DB: UPDATE facturas SET uuid_sat = '12345...', estado = 'Timbrada'
        Backend-->>Billing: ✅ Factura timbrada (UUID: 12345...)
        Billing->>User: Botón "Descargar PDF" habilitado
    else Error en SAT
        SAT-->>Backend: Error: RFC inválido
        Backend-->>Billing: ❌ Error al timbrar factura
        Billing->>User: Mostrar error y reintentar
    end
```

---

## 🔄 Diagrama 6: FLUJO 4 - Inventario → Tratamiento → Finanzas

```mermaid
graph TD
    subgraph MedicalAttention["🩺 Medical Attention"]
        SelectTreatment[Seleccionar Tratamiento]
        SelectMaterials[Seleccionar Materiales Usados]
        SaveTreatment[Guardar Tratamiento]
    end
    
    subgraph Backend["⚙️ Backend"]
        ProcessTreatment[POST /api/tratamientos]
        UpdateInventory[Actualizar Inventario]
        LogMovement[Registrar Movimiento]
    end
    
    subgraph Database["🗄️ Base de Datos"]
        DetalleCita[(detalle_cita)]
        MaterialesUsados[(materiales_usados)]
        Inventario[(inventario)]
        MovimientosInv[(movimientos_inventario)]
        Gastos[(gastos)]
    end
    
    subgraph Inventory["📦 Admin Inventory"]
        StockLevel[Stock Actual: 48]
        LowStockAlert[⚠️ Alerta: Stock Bajo]
    end
    
    subgraph Finances["💵 Finances"]
        DailyClose[Corte de Caja del Día]
        IncomeCalc[Ingresos: $5,250]
        ExpensesCalc[Gastos: $1,120 incluye materiales]
        ProfitCalc[Utilidad: $4,130]
    end
    
    SelectTreatment --> SelectMaterials
    SelectMaterials -->|"2x Vendas estériles"| SaveTreatment
    SaveTreatment --> ProcessTreatment
    
    ProcessTreatment --> DetalleCita
    ProcessTreatment --> MaterialesUsados
    
    MaterialesUsados -->|"cantidad_usada: 2<br/>costo: $15.50 c/u"| UpdateInventory
    
    UpdateInventory -->|"stock_actual - 2"| Inventario
    UpdateInventory --> LogMovement
    
    LogMovement --> MovimientosInv
    MovimientosInv -->|"tipo: Salida<br/>motivo: Tratamiento"| Gastos
    
    Inventario -->|"IF stock < stock_minimo"| LowStockAlert
    LowStockAlert -.->|WebSocket notify| Inventory
    
    Inventario -->|Auto-refresh| StockLevel
    
    Gastos -->|"SUM(monto)"| ExpensesCalc
    ExpensesCalc --> DailyClose
    IncomeCalc --> DailyClose
    DailyClose --> ProfitCalc
    
    style LowStockAlert fill:#ffcdd2
    style ProfitCalc fill:#c8e6c9
    style StockLevel fill:#fff9c4
```

---

## 🔄 Diagrama 7: FLUJO 5 - Dashboard Agregaciones Multi-Tabla

```mermaid
graph TB
    subgraph Dashboard["📊 /dashboard"]
        KPICards[KPI Cards]
        Charts[Gráficas Interactivas]
        Alerts[Alertas del Sistema]
    end
    
    subgraph Backend["⚙️ Backend API"]
        StatsEndpoint[GET /api/stats/dashboard]
        AggregateQueries[Queries de Agregación]
    end
    
    subgraph MaterializedView["🗄️ Vista Materializada"]
        DashboardKPIs[(dashboard_kpis)]
        RefreshSchedule[REFRESH cada hora]
    end
    
    subgraph SourceTables["🗄️ Tablas Fuente"]
        Citas[(citas)]
        Pacientes[(pacientes)]
        Pagos[(pagos)]
        Inventario[(inventario)]
        Usuarios[(usuarios)]
        DetalleCita[(detalle_cita)]
        Tratamientos[(tratamientos)]
    end
    
    Dashboard -->|useEffect| StatsEndpoint
    StatsEndpoint --> AggregateQueries
    
    AggregateQueries -->|SELECT * FROM| DashboardKPIs
    
    Citas -->|COUNT, GROUP BY| DashboardKPIs
    Pacientes -->|COUNT DISTINCT| DashboardKPIs
    Pagos -->|SUM(monto_total)| DashboardKPIs
    Inventario -->|WHERE stock < stock_min| DashboardKPIs
    Usuarios -->|JOIN podologos| DashboardKPIs
    DetalleCita -->|JOIN| DashboardKPIs
    Tratamientos -->|COUNT, GROUP BY| DashboardKPIs
    
    RefreshSchedule -.->|Programado| DashboardKPIs
    
    DashboardKPIs -->|Response JSON| StatsEndpoint
    StatsEndpoint -->|Data| KPICards
    
    KPICards -->|"📅 Citas Hoy: 18"| Dashboard
    KPICards -->|"👥 Pacientes: 15 (3 nuevos)"| Dashboard
    KPICards -->|"💰 Ingresos: $8,450"| Dashboard
    KPICards -->|"📦 Alertas: 4 productos"| Dashboard
    
    DashboardKPIs -->|Chart Data| Charts
    Charts -->|Bar Chart| Dashboard
    Charts -->|Line Chart| Dashboard
    Charts -->|Pie Chart| Dashboard
    
    DashboardKPIs -->|Critical Items| Alerts
    
    style KPICards fill:#e3f2fd
    style Alerts fill:#ffebee
    style DashboardKPIs fill:#f3e5f5
```

---

## 🔄 Diagrama 8: Sincronización Real-Time entre Pestañas

```mermaid
sequenceDiagram
    participant Calendar as 📅 /calendar
    participant Backend as ⚙️ Backend
    participant DB as 🗄️ PostgreSQL
    participant WS as 🔌 WebSocket Server
    participant Dashboard as 📊 /dashboard
    participant Patients as 👥 /patients
    
    Note over Calendar,Patients: Usuario crea nueva cita en /calendar
    
    Calendar->>Backend: POST /api/citas {paciente: 567, fecha: "2026-01-15 10:00"}
    Backend->>DB: INSERT INTO citas (id_paciente, fecha_hora_inicio, ...)
    DB-->>Backend: citas.id = 2000 ✅
    
    Backend->>WS: broadcast("nueva_cita_creada", {id: 2000, paciente: 567})
    
    par WebSocket Broadcast
        WS->>Dashboard: event: "nueva_cita_creada"
        and
        WS->>Patients: event: "nueva_cita_creada"
        and
        WS->>Calendar: event: "nueva_cita_creada"
    end
    
    rect rgb(200, 230, 255)
        Dashboard->>Dashboard: Incrementar counter "Citas Hoy": 18 → 19
        Note over Dashboard: KPI actualizado en tiempo real
    end
    
    rect rgb(255, 230, 200)
        Patients->>Patients: Actualizar "Próximas Citas" del paciente 567
        Note over Patients: Lista de citas refrescada
    end
    
    rect rgb(200, 255, 230)
        Calendar->>Calendar: Agregar nueva cita al calendario visual
        Note over Calendar: Evento aparece en la vista semanal
    end
    
    Note over Calendar,Patients: Sincronización completada sin recargar página
```

---

## 🔄 Diagrama 9: Patrones de Actualización Reactiva

```mermaid
graph TB
    subgraph Pattern1["Patrón 1: Cascada WebSocket"]
        Action1[Acción en Pestaña A]
        Backend1[Backend procesa]
        DB1[Base de Datos actualizada]
        WS1[WebSocket broadcast]
        Update1[Pestañas B, C, D actualizan]
        
        Action1 --> Backend1 --> DB1 --> WS1 --> Update1
    end
    
    subgraph Pattern2["Patrón 2: Polling de Estado"]
        Component2[Componente React]
        Interval2[setInterval 5s]
        Check2[fetchStatus]
        Condition2{Estado cambió?}
        Update2[Actualizar UI]
        
        Component2 --> Interval2 --> Check2 --> Condition2
        Condition2 -->|Sí| Update2
        Condition2 -->|No| Interval2
    end
    
    subgraph Pattern3["Patrón 3: React Query Cache"]
        Query3[useQuery 'patient-567']
        Cache3[Cache local]
        Mutation3[Guardar alergia]
        Invalidate3[invalidateQueries]
        Refetch3[Re-fetch automático]
        
        Query3 --> Cache3
        Mutation3 --> Invalidate3 --> Refetch3
        Refetch3 --> Cache3
    end
    
    subgraph Pattern4["Patrón 4: Context API Global"]
        Context4[GlobalContext]
        Provider4[Provider wrapper]
        Consumer1[/calendar]
        Consumer2[/patients]
        Consumer3[/dashboard]
        
        Provider4 --> Context4
        Context4 -.compartido.-> Consumer1
        Context4 -.compartido.-> Consumer2
        Context4 -.compartido.-> Consumer3
    end
    
    style Pattern1 fill:#e3f2fd
    style Pattern2 fill:#fff3e0
    style Pattern3 fill:#f3e5f5
    style Pattern4 fill:#c8e6c9
```

---

## 📋 Diagrama 10: Mapa de Impactos Cross-Module

```mermaid
mindmap
  root((Cambios<br/>Cross-Module))
    Calendario
      Crear Cita
        Dashboard: +1 cita
        Patients: Próxima cita
        Finances: +Ingreso proyectado
      Cancelar Cita
        Dashboard: -1 cita pendiente
        Patients: Cita cancelada
        Finances: -Ingreso proyectado
      Completar Cita
        Medical: Abrir expediente
        Billing: Facturar
        Dashboard: +1 completada
    
    Pacientes
      Agregar Alergia
        Medical: Banner alerta ⚠️
        Records: Historial actualizado
        Dashboard: +1 alerta crítica
      Asignar Podólogo
        Calendar: Auto-sugerencia
        Dashboard: Stats por podólogo
        Medical: Filtro expedientes
      Editar Datos
        Calendar: Nombre actualizado
        Billing: RFC correcto
        Medical: Info correcta
    
    Admin
      Actualizar Precio Servicio
        Calendar: Nuevo precio
        Medical: Cálculo correcto
        Billing: Factura correcta
        Dashboard: Proyección ajustada
      Inventario Bajo Stock
        Admin: Badge rojo ⚠️
        Dashboard: Alerta crítica
        Medical: Warning tooltip
        Finances: Orden de compra sugerida
      Agregar Personal
        Calendar: Nuevo filtro
        Dashboard: Nueva estadística
        Admin: Lista actualizada
    
    Facturación
      Registrar Pago
        Finances: +Ingreso real
        Dashboard: Cobrado hoy
        Patients: Estado pagado
      Timbrar Factura
        Billing: UUID SAT ✅
        Finances: Facturado legal
        Patients: Historial pagos
      Cancelar Factura
        SAT: CFDI cancelado
        Finances: Ajuste contable
        Dashboard: Recálculo
```

---

## 🔍 Diagrama 11: Ejemplo Concreto - Agregar Alergia a Paciente

```mermaid
flowchart TD
    Start([👨‍💼 Usuario en /patients]) --> OpenPatient[Abrir paciente #567]
    OpenPatient --> EditButton[Click: Editar → Alergias]
    EditButton --> AddAllergy[Agregar: Penicilina - Severa]
    AddAllergy --> SaveButton[Click: Guardar]
    
    SaveButton --> Backend[POST /api/pacientes/567/alergias]
    Backend --> DBInsert[INSERT INTO alergias]
    
    DBInsert --> Success{Guardado<br/>exitoso?}
    
    Success -->|Sí| WSBroadcast[WebSocket: alergia_agregada]
    Success -->|No| ErrorMsg[Mostrar error]
    
    WSBroadcast --> Multiple[Actualizar múltiples pestañas]
    
    Multiple --> PatientsUpdate[📋 /patients<br/>Lista de alergias actualizada]
    Multiple --> MedicalUpdate[🩺 /medical/attention<br/>Banner alerta rojo ⚠️]
    Multiple --> RecordsUpdate[📋 /medical/records<br/>Sección alergias refrescada]
    Multiple --> DashboardUpdate[📊 /dashboard<br/>+1 Alerta crítica]
    
    PatientsUpdate --> End1([✅ UI Actualizada])
    MedicalUpdate --> End2([⚠️ Alerta Visible])
    RecordsUpdate --> End3([📝 Expediente OK])
    DashboardUpdate --> End4([📊 KPI +1])
    
    style AddAllergy fill:#fff9c4
    style DBInsert fill:#c8e6c9
    style WSBroadcast fill:#e1bee7
    style MedicalUpdate fill:#ffcdd2
    style ErrorMsg fill:#ef9a9a
```

---

## 🎯 Diagrama 12: Estados de una Cita (State Machine)

```mermaid
stateDiagram-v2
    [*] --> Pendiente: Crear cita<br/>(Calendar)
    
    Pendiente --> Confirmada: Confirmar<br/>(Phone/WhatsApp)
    Pendiente --> Cancelada: Cancelar<br/>(Calendar)
    
    Confirmada --> En_Curso: Iniciar atención<br/>(Medical Attention)
    Confirmada --> No_Asistio: Paciente no llegó<br/>(Calendar)
    Confirmada --> Cancelada: Cancelar<br/>(Calendar/WhatsApp)
    
    En_Curso --> Completada: Finalizar atención<br/>(Medical Attention)
    
    Completada --> Facturacion: Ir a facturación<br/>(Billing)
    Facturacion --> Pagada: Registrar pago<br/>(Billing)
    Pagada --> Facturada: Timbrar CFDI<br/>(SAT API)
    
    Cancelada --> [*]: Registro en historial
    No_Asistio --> [*]: Registro en historial
    Facturada --> [*]: Proceso completo ✅
    
    note right of Pendiente
        Frontend: /calendar
        Badge: Azul
        Acciones: Editar, Cancelar, Confirmar
    end note
    
    note right of En_Curso
        Frontend: /medical/attention
        Badge: Verde pulsante
        Acciones: Registrar signos vitales,
        Diagnosticar, Prescribir
    end note
    
    note right of Completada
        Frontend: /billing
        Badge: Verde
        Acciones: Registrar pago,
        Generar factura
    end note
    
    note right of Facturada
        Frontend: /finances
        Badge: Verde con check ✅
        Acciones: Descargar PDF,
        Enviar por email
    end note
```

---

## 📊 Resumen de Tecnologías Utilizadas

```mermaid
graph LR
    subgraph Frontend["Frontend Stack"]
        React[React 18]
        TS[TypeScript]
        Vite[Vite]
        TailwindCSS[TailwindCSS]
        ReactQuery[React Query]
    end
    
    subgraph Backend["Backend Stack"]
        FastAPI[FastAPI]
        Python[Python 3.11+]
        AsyncPG[AsyncPG]
        LangGraph[LangGraph]
        Redis[Redis]
    end
    
    subgraph Database["Database"]
        PostgreSQL[PostgreSQL 14+]
        PgVector[pgvector]
        MaterializedViews[Materialized Views]
    end
    
    subgraph RealTime["Real-Time"]
        WebSockets[WebSockets]
        SSE[Server-Sent Events]
    end
    
    React --> FastAPI
    FastAPI --> PostgreSQL
    FastAPI --> Redis
    PostgreSQL --> MaterializedViews
    
    ReactQuery --> WebSockets
    WebSockets --> FastAPI
    
    style Frontend fill:#61dafb,color:#000
    style Backend fill:#009688,color:#fff
    style Database fill:#336791,color:#fff
    style RealTime fill:#ff6b6b,color:#fff
```

---

## 📝 Convenciones de los Diagramas

### Colores:
- 🔵 **Azul claro** (#e3f2fd): Frontend/UI
- 🟠 **Naranja claro** (#fff3e0): Backend/API
- 🟣 **Púrpura claro** (#f3e5f5): Base de Datos
- 🟢 **Verde claro** (#c8e6c9): Operación exitosa
- 🔴 **Rojo claro** (#ffcdd2): Alertas/Errores
- 🟡 **Amarillo claro** (#fff9c4): En proceso/Pendiente

### Símbolos:
- `FK` = Foreign Key (Llave Foránea)
- `PK` = Primary Key (Llave Primaria)
- `UK` = Unique Key (Llave Única)
- `→` = Flujo de datos
- `-.->` = Relación indirecta/notificación
- `⚠️` = Alerta o advertencia
- `✅` = Operación exitosa
- `❌` = Error o fallo

### Iconos de Módulos:
- 📅 Calendar (Calendario)
- 🩺 Medical (Atención Médica)
- 📋 Records (Expedientes)
- 👥 Patients (Pacientes)
- 📊 Dashboard (Panel)
- 💰 Billing (Facturación)
- 💵 Finances (Finanzas)
- ⚙️ Admin (Administración)
- 🗄️ Database (Base de Datos)
- 🔌 WebSocket (Tiempo Real)
