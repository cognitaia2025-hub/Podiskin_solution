# Agente 14: Generador de Datos Mock de Pacientes - Mexicali/Calexico

## Metadata
- **Agent ID**: agent-14-dev-mock-data-pacientes
- **Version**: 1.0.0
- **Category**: Development/Testing
- **Priority**: Medium
- **Status**: Active
- **Created**: 2026-01-01
- **Last Updated**: 2026-01-01

## Propósito
Generar 200 registros de pacientes mock con datos demográficos realistas para las regiones de Mexicali, Baja California (México) y Calexico, California (EUA), incluyendo información completa de alergias, antecedentes médicos, condiciones crónicas y datos de contacto para propósitos de desarrollo y testing.

## Contexto del Proyecto
Este agente es parte del sistema Podiskin y genera datos de prueba realistas que reflejan la demografía binacional de la región Mexicali-Calexico, incluyendo:
- Diversidad étnica y cultural
- Nombres hispanos y anglosajones apropiados
- Direcciones reales de ambas ciudades
- Condiciones médicas prevalentes en la región
- Factores de riesgo comunes en poblaciones fronterizas

## Especificaciones Técnicas

### Distribución Geográfica
- **60% Mexicali, BC**: Colonias representativas
- **40% Calexico, CA**: Zonas residenciales típicas

### Distribución Demográfica

#### Por Edad
- 0-17 años: 20% (40 pacientes)
- 18-35 años: 25% (50 pacientes)
- 36-55 años: 30% (60 pacientes)
- 56-75 años: 20% (40 pacientes)
- 76+ años: 5% (10 pacientes)

#### Por Género
- Femenino: 52% (104 pacientes)
- Masculino: 47% (94 pacientes)
- No binario/Otro: 1% (2 pacientes)

#### Por Etnicidad
- Hispano/Latino: 85% (170 pacientes)
- Caucásico no hispano: 10% (20 pacientes)
- Otro: 5% (10 pacientes)

### Estructura de Datos por Paciente

```typescript
interface PatientMockData {
  // Identificación
  patientId: string;              // UUID v4
  mrn: string;                    // Medical Record Number (8 dígitos)
  
  // Datos Personales
  firstName: string;
  middleName?: string;
  lastName: string;
  secondLastName?: string;        // Para pacientes mexicanos
  preferredName?: string;
  dateOfBirth: Date;
  age: number;
  gender: 'M' | 'F' | 'NB' | 'O';
  biologicalSex: 'M' | 'F';
  
  // Demografía
  ethnicity: string;
  race: string[];
  primaryLanguage: 'es' | 'en' | 'es-en';
  secondaryLanguages?: string[];
  
  // Contacto
  email: string;
  phoneNumber: string;
  alternatePhone?: string;
  
  // Dirección
  address: {
    street: string;
    colonia?: string;             // Para direcciones mexicanas
    city: 'Mexicali' | 'Calexico';
    state: 'Baja California' | 'California';
    country: 'México' | 'USA';
    zipCode: string;
    coordinates?: {
      lat: number;
      lng: number;
    };
  };
  
  // Información de Seguro
  insurance: {
    provider: string;
    policyNumber: string;
    groupNumber?: string;
    effectiveDate: Date;
    expirationDate: Date;
    copay?: number;
  }[];
  
  // Contacto de Emergencia
  emergencyContact: {
    name: string;
    relationship: string;
    phone: string;
    alternatePhone?: string;
  };
  
  // Información Médica
  bloodType: string;
  height: number;                 // cm
  weight: number;                 // kg
  bmi: number;
  
  // Alergias
  allergies: {
    allergen: string;
    type: 'medication' | 'food' | 'environmental' | 'other';
    severity: 'mild' | 'moderate' | 'severe' | 'life-threatening';
    reaction: string[];
    onsetDate?: Date;
    notes?: string;
  }[];
  
  // Condiciones Crónicas
  chronicConditions: {
    condition: string;
    icd10Code: string;
    diagnosisDate: Date;
    status: 'active' | 'controlled' | 'in-remission' | 'resolved';
    treatingProvider?: string;
    notes?: string;
  }[];
  
  // Medicamentos Actuales
  medications: {
    name: string;
    genericName?: string;
    dosage: string;
    frequency: string;
    route: string;
    prescribedDate: Date;
    prescribedBy: string;
    indication: string;
    status: 'active' | 'discontinued' | 'on-hold';
  }[];
  
  // Antecedentes Médicos
  medicalHistory: {
    surgeries: {
      procedure: string;
      date: Date;
      hospital: string;
      surgeon?: string;
      complications?: string;
    }[];
    hospitalizations: {
      reason: string;
      admissionDate: Date;
      dischargeDate: Date;
      hospital: string;
      notes?: string;
    }[];
    familyHistory: {
      relationship: string;
      condition: string;
      ageAtDiagnosis?: number;
      deceased?: boolean;
      causeOfDeath?: string;
    }[];
  };
  
  // Hábitos y Estilo de Vida
  socialHistory: {
    smokingStatus: 'never' | 'former' | 'current';
    packsPerDay?: number;
    yearsSmoked?: number;
    quitDate?: Date;
    
    alcoholUse: 'never' | 'occasional' | 'moderate' | 'heavy';
    drinksPerWeek?: number;
    
    exerciseFrequency: 'sedentary' | 'light' | 'moderate' | 'active' | 'very-active';
    occupation?: string;
    maritalStatus: 'single' | 'married' | 'divorced' | 'widowed' | 'domestic-partnership';
  };
  
  // Signos Vitales Recientes
  lastVitals?: {
    date: Date;
    bloodPressureSystolic: number;
    bloodPressureDiastolic: number;
    heartRate: number;
    temperature: number;          // Celsius
    respiratoryRate: number;
    oxygenSaturation: number;
  };
  
  // Metadata
  registrationDate: Date;
  lastVisitDate?: Date;
  nextAppointmentDate?: Date;
  primaryCareProvider?: string;
  preferredClinic: string;
  
  // Flags
  isActive: boolean;
  isHighRisk: boolean;
  requiresInterpreter: boolean;
  hasAdvanceDirective: boolean;
  isDNR: boolean;
}
```

## Datos Realistas por Región

### Colonias de Mexicali (60% de pacientes)
- Centro Cívico
- Nueva Esperanza
- Pro-Hogar
- Cuauhtémoc Sur
- Rivera Campestre
- Industrial
- Hidalgo
- Juárez
- Pueblo Nuevo
- Santa Isabel
- Jardines del Valle
- Las Fuentes

### Zonas de Calexico (40% de pacientes)
- Downtown Calexico
- Nosotros
- Villa del Sol
- Kennedy Gardens
- Cole District
- Westside
- Eastside
- Rockwood

### Proveedores de Seguro Comunes
**México (Mexicali)**:
- IMSS (Instituto Mexicano del Seguro Social)
- ISSSTE (Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado)
- Seguro Popular / INSABI
- AXA Seguros
- GNP Seguros
- Metlife México
- Sin seguro (15% de pacientes mexicanos)

**USA (Calexico)**:
- Medicare
- Medi-Cal (Medicaid)
- Blue Cross Blue Shield
- Health Net
- Molina Healthcare
- Kaiser Permanente
- United Healthcare
- Sin seguro (8% de pacientes estadounidenses)

### Condiciones Médicas Prevalentes en la Región

#### Muy Comunes (20-30% de pacientes)
- Diabetes Mellitus Tipo 2 (E11)
- Hipertensión Arterial (I10)
- Obesidad (E66)
- Dislipidemia (E78)

#### Comunes (10-20%)
- Asma (J45)
- Enfermedad por Reflujo Gastroesofágico (K21)
- Artritis/Osteoartritis (M19)
- Depresión (F33)
- Ansiedad (F41)

#### Moderadamente Comunes (5-10%)
- Enfermedad Renal Crónica (N18)
- Hipotiroidismo (E03)
- Enfermedad Pulmonar Obstructiva Crónica (J44)
- Migraña (G43)
- Insuficiencia Venosa (I87.2)

#### Relacionadas con Podología (15-25% de pacientes)
- Pie Diabético (E11.621)
- Onicomicosis (B35.1)
- Fascitis Plantar (M72.2)
- Neuropatía Periférica (G62.9)
- Úlceras del Pie (L97)
- Deformidades del Pie (M21.0-M21.9)
- Callos y Callosidades (L84)

### Alergias Comunes
**Medicamentos**:
- Penicilina (10% de pacientes)
- Sulfonamidas (3%)
- AINEs (5%)
- Codeína/Opioides (4%)
- Látex (2%)

**Alimentos**:
- Mariscos (3%)
- Nueces (2%)
- Lactosa (8%)
- Gluten (2%)

**Ambientales**:
- Polen de mezquite (15%)
- Ácaros del polvo (12%)
- Caspa de mascotas (8%)
- Moho (5%)

## Nombres Realistas

### Nombres Hispanos Masculinos
- Miguel, José, Juan, Luis, Carlos, Francisco, Antonio, Jesús, Pedro, Roberto, Jorge, Rafael, Eduardo, Raúl, Sergio, Fernando, Mario, Ricardo, Alberto, Alejandro

### Nombres Hispanos Femeninos
- María, Guadalupe, Juana, Rosa, Ana, Francisca, Elena, Teresa, Carmen, Lucía, Patricia, Verónica, Gabriela, Claudia, Silvia, Daniela, Alejandra, Mónica, Laura, Isabel

### Apellidos Hispanos Comunes
- García, Rodríguez, Martínez, Hernández, López, González, Pérez, Sánchez, Ramírez, Torres, Flores, Rivera, Gómez, Díaz, Reyes, Cruz, Morales, Gutiérrez, Ortiz, Mendoza, Jiménez, Ruiz, Castillo, Romero, Vargas

### Nombres Anglosajones (para 15% de pacientes)
**Masculinos**: Michael, John, David, Robert, James, William, Richard, Thomas, Christopher, Daniel
**Femeninos**: Mary, Patricia, Jennifer, Linda, Barbara, Elizabeth, Susan, Jessica, Sarah, Karen
**Apellidos**: Smith, Johnson, Williams, Brown, Jones, Miller, Davis, Wilson, Anderson, Taylor

## Hospitales y Clínicas de Referencia

### Mexicali
- Hospital General de Mexicali
- Hospital de Especialidades del IMSS
- Hospital Materno Infantil
- Hospital Almater
- Clínica Hospital del ISSSTE
- Hospital Hispano Americano

### Calexico/Imperial Valley
- Calexico Health Center
- Clinicas de Salud del Pueblo
- El Centro Regional Medical Center
- Pioneers Memorial Healthcare District
- Imperial Valley Family Care

## Generación de Datos

### Script de Generación (TypeScript/Node.js)

```typescript
import { faker } from '@faker-js/faker';
import { v4 as uuidv4 } from 'uuid';

// Configurar faker para español
faker.locale = 'es_MX';

class PatientMockDataGenerator {
  private mexicoPercentage = 0.6;
  private femalePercentage = 0.52;
  
  // Arrays de datos realistas
  private mexicaliColonias = [
    'Centro Cívico', 'Nueva Esperanza', 'Pro-Hogar', 
    'Cuauhtémoc Sur', 'Rivera Campestre', 'Industrial',
    'Hidalgo', 'Juárez', 'Pueblo Nuevo', 'Santa Isabel'
  ];
  
  private calexicoZones = [
    'Downtown', 'Nosotros', 'Villa del Sol', 
    'Kennedy Gardens', 'Cole District', 'Westside'
  ];
  
  private hispanicFirstNamesMale = [
    'Miguel', 'José', 'Juan', 'Luis', 'Carlos', 'Francisco',
    'Antonio', 'Jesús', 'Pedro', 'Roberto', 'Jorge', 'Rafael'
  ];
  
  private hispanicFirstNamesFemale = [
    'María', 'Guadalupe', 'Juana', 'Rosa', 'Ana', 'Francisca',
    'Elena', 'Teresa', 'Carmen', 'Lucía', 'Patricia', 'Verónica'
  ];
  
  private hispanicLastNames = [
    'García', 'Rodríguez', 'Martínez', 'Hernández', 'López',
    'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres'
  ];
  
  private chronicConditionsPool = [
    { condition: 'Diabetes Mellitus Type 2', icd10: 'E11', prevalence: 0.25 },
    { condition: 'Hypertension', icd10: 'I10', prevalence: 0.30 },
    { condition: 'Obesity', icd10: 'E66', prevalence: 0.28 },
    { condition: 'Dyslipidemia', icd10: 'E78', prevalence: 0.22 },
    { condition: 'Asthma', icd10: 'J45', prevalence: 0.12 },
    { condition: 'GERD', icd10: 'K21', prevalence: 0.15 },
    { condition: 'Osteoarthritis', icd10: 'M19', prevalence: 0.18 },
    { condition: 'Depression', icd10: 'F33', prevalence: 0.14 },
    { condition: 'Diabetic Foot', icd10: 'E11.621', prevalence: 0.08 },
    { condition: 'Plantar Fasciitis', icd10: 'M72.2', prevalence: 0.10 }
  ];
  
  private allergiesPool = [
    { 
      allergen: 'Penicillin', 
      type: 'medication', 
      reactions: ['Rash', 'Hives', 'Itching'],
      prevalence: 0.10 
    },
    { 
      allergen: 'Mesquite Pollen', 
      type: 'environmental', 
      reactions: ['Sneezing', 'Runny nose', 'Itchy eyes'],
      prevalence: 0.15 
    },
    { 
      allergen: 'NSAIDs', 
      type: 'medication', 
      reactions: ['Gastric upset', 'Rash'],
      prevalence: 0.05 
    },
    { 
      allergen: 'Shellfish', 
      type: 'food', 
      reactions: ['Hives', 'Swelling', 'Difficulty breathing'],
      prevalence: 0.03 
    },
    { 
      allergen: 'Dust Mites', 
      type: 'environmental', 
      reactions: ['Sneezing', 'Coughing', 'Wheezing'],
      prevalence: 0.12 
    }
  ];

  generatePatients(count: number = 200): PatientMockData[] {
    const patients: PatientMockData[] = [];
    
    for (let i = 0; i < count; i++) {
      patients.push(this.generatePatient(i));
    }
    
    return patients;
  }
  
  private generatePatient(index: number): PatientMockData {
    const isMexico = Math.random() < this.mexicoPercentage;
    const isFemale = Math.random() < this.femalePercentage;
    const isHispanic = Math.random() < 0.85;
    
    const age = this.generateAgeByDistribution();
    const dateOfBirth = this.calculateDateOfBirth(age);
    
    // Generar nombre
    const name = this.generateName(isFemale, isHispanic, isMexico);
    
    // Generar dirección
    const address = this.generateAddress(isMexico);
    
    // Generar datos médicos
    const height = this.generateHeight(isFemale);
    const weight = this.generateWeight(age, isFemale);
    const bmi = this.calculateBMI(weight, height);
    
    const allergies = this.generateAllergies();
    const chronicConditions = this.generateChronicConditions(age, bmi);
    const medications = this.generateMedications(chronicConditions);
    
    return {
      patientId: uuidv4(),
      mrn: this.generateMRN(),
      
      ...name,
      dateOfBirth,
      age,
      gender: isFemale ? 'F' : 'M',
      biologicalSex: isFemale ? 'F' : 'M',
      
      ethnicity: isHispanic ? 'Hispanic or Latino' : 'Not Hispanic or Latino',
      race: isHispanic ? ['Other Race'] : ['White'],
      primaryLanguage: this.determinePrimaryLanguage(isMexico, isHispanic),
      secondaryLanguages: this.determineSecondaryLanguages(isMexico),
      
      email: this.generateEmail(name.firstName, name.lastName),
      phoneNumber: this.generatePhone(isMexico),
      
      address,
      
      insurance: this.generateInsurance(isMexico, age),
      
      emergencyContact: this.generateEmergencyContact(isHispanic),
      
      bloodType: this.generateBloodType(),
      height,
      weight,
      bmi,
      
      allergies,
      chronicConditions,
      medications,
      
      medicalHistory: this.generateMedicalHistory(age),
      socialHistory: this.generateSocialHistory(age),
      
      lastVitals: this.generateVitals(chronicConditions),
      
      registrationDate: this.generateRegistrationDate(),
      lastVisitDate: this.generateLastVisitDate(),
      primaryCareProvider: this.generateProviderName(isHispanic),
      preferredClinic: this.getPreferredClinic(isMexico),
      
      isActive: true,
      isHighRisk: this.determineHighRisk(age, chronicConditions, bmi),
      requiresInterpreter: this.requiresInterpreter(isMexico, isHispanic),
      hasAdvanceDirective: age > 65 && Math.random() < 0.4,
      isDNR: age > 75 && Math.random() < 0.15
    };
  }
  
  private generateAgeByDistribution(): number {
    const rand = Math.random();
    
    if (rand < 0.20) {
      // 0-17 años
      return Math.floor(Math.random() * 18);
    } else if (rand < 0.45) {
      // 18-35 años
      return 18 + Math.floor(Math.random() * 18);
    } else if (rand < 0.75) {
      // 36-55 años
      return 36 + Math.floor(Math.random() * 20);
    } else if (rand < 0.95) {
      // 56-75 años
      return 56 + Math.floor(Math.random() * 20);
    } else {
      // 76+ años
      return 76 + Math.floor(Math.random() * 15);
    }
  }
  
  private calculateDateOfBirth(age: number): Date {
    const today = new Date();
    const year = today.getFullYear() - age;
    const month = Math.floor(Math.random() * 12);
    const day = Math.floor(Math.random() * 28) + 1;
    return new Date(year, month, day);
  }
  
  private generateName(isFemale: boolean, isHispanic: boolean, isMexico: boolean) {
    let firstName: string;
    let lastName: string;
    let secondLastName: string | undefined;
    
    if (isHispanic) {
      firstName = isFemale 
        ? this.randomFromArray(this.hispanicFirstNamesFemale)
        : this.randomFromArray(this.hispanicFirstNamesMale);
      lastName = this.randomFromArray(this.hispanicLastNames);
      
      if (isMexico) {
        secondLastName = this.randomFromArray(this.hispanicLastNames);
      }
    } else {
      firstName = isFemale ? faker.name.firstName('female') : faker.name.firstName('male');
      lastName = faker.name.lastName();
    }
    
    return {
      firstName,
      lastName,
      secondLastName,
      middleName: Math.random() < 0.3 ? faker.name.middleName() : undefined
    };
  }
  
  private generateAddress(isMexico: boolean) {
    if (isMexico) {
      return {
        street: `${faker.address.streetName()} ${faker.datatype.number({ min: 100, max: 9999 })}`,
        colonia: this.randomFromArray(this.mexicaliColonias),
        city: 'Mexicali' as const,
        state: 'Baja California' as const,
        country: 'México' as const,
        zipCode: `2190${faker.datatype.number({ min: 0, max: 9 })}`,
        coordinates: {
          lat: 32.6245 + (Math.random() - 0.5) * 0.1,
          lng: -115.4523 + (Math.random() - 0.5) * 0.1
        }
      };
    } else {
      return {
        street: `${faker.datatype.number({ min: 100, max: 2000 })} ${faker.address.streetName()}`,
        city: 'Calexico' as const,
        state: 'California' as const,
        country: 'USA' as const,
        zipCode: '92231',
        coordinates: {
          lat: 32.6789 + (Math.random() - 0.5) * 0.05,
          lng: -115.4989 + (Math.random() - 0.5) * 0.05
        }
      };
    }
  }
  
  private generateMRN(): string {
    return faker.datatype.number({ min: 10000000, max: 99999999 }).toString();
  }
  
  private generateHeight(isFemale: boolean): number {
    // En centímetros
    const base = isFemale ? 160 : 175;
    const variance = 15;
    return Math.round(base + (Math.random() - 0.5) * variance);
  }
  
  private generateWeight(age: number, isFemale: boolean): number {
    // En kilogramos
    const baseWeight = isFemale ? 65 : 80;
    const ageAdjustment = age > 50 ? 5 : 0;
    const variance = 25;
    return Math.round(baseWeight + ageAdjustment + (Math.random() - 0.3) * variance);
  }
  
  private calculateBMI(weight: number, height: number): number {
    const heightInMeters = height / 100;
    return Math.round((weight / (heightInMeters * heightInMeters)) * 10) / 10;
  }
  
  private generateAllergies() {
    const allergies: any[] = [];
    
    for (const allergyTemplate of this.allergiesPool) {
      if (Math.random() < allergyTemplate.prevalence) {
        allergies.push({
          allergen: allergyTemplate.allergen,
          type: allergyTemplate.type,
          severity: this.randomFromArray(['mild', 'moderate', 'severe']),
          reaction: allergyTemplate.reactions,
          onsetDate: this.generatePastDate(20)
        });
      }
    }
    
    return allergies;
  }
  
  private generateChronicConditions(age: number, bmi: number) {
    const conditions: any[] = [];
    
    for (const conditionTemplate of this.chronicConditionsPool) {
      let adjustedPrevalence = conditionTemplate.prevalence;
      
      // Ajustar prevalencia por edad
      if (age > 50) adjustedPrevalence *= 1.5;
      if (age > 65) adjustedPrevalence *= 1.8;
      
      // Ajustar por BMI
      if (bmi > 30) adjustedPrevalence *= 1.3;
      
      if (Math.random() < adjustedPrevalence) {
        conditions.push({
          condition: conditionTemplate.condition,
          icd10Code: conditionTemplate.icd10,
          diagnosisDate: this.generatePastDate(15),
          status: this.randomFromArray(['active', 'controlled', 'controlled']), // Más probabilidad de controlado
          treatingProvider: this.generateProviderName(Math.random() < 0.85)
        });
      }
    }
    
    return conditions;
  }
  
  private generateMedications(chronicConditions: any[]) {
    const medications: any[] = [];
    
    // Mapeo de condiciones a medicamentos
    const medicationMap: Record<string, string[]> = {
      'E11': ['Metformin 500mg', 'Glipizide 5mg', 'Insulin Glargine'],
      'I10': ['Lisinopril 10mg', 'Amlodipine 5mg', 'Losartan 50mg'],
      'E78': ['Atorvastatin 20mg', 'Simvastatin 40mg'],
      'J45': ['Albuterol Inhaler', 'Fluticasone Inhaler'],
      'F33': ['Sertraline 50mg', 'Escitalopram 10mg']
    };
    
    for (const condition of chronicConditions) {
      const meds = medicationMap[condition.icd10Code];
      if (meds && meds.length > 0) {
        const selectedMed = this.randomFromArray(meds);
        medications.push({
          name: selectedMed,
          dosage: selectedMed.split(' ')[1] || '1 tablet',
          frequency: 'Once daily',
          route: 'Oral',
          prescribedDate: condition.diagnosisDate,
          prescribedBy: condition.treatingProvider,
          indication: condition.condition,
          status: 'active'
        });
      }
    }
    
    return medications;
  }
  
  private generateMedicalHistory(age: number) {
    return {
      surgeries: [],
      hospitalizations: [],
      familyHistory: this.generateFamilyHistory()
    };
  }
  
  private generateFamilyHistory() {
    const conditions = [
      'Diabetes', 'Hypertension', 'Heart Disease', 
      'Cancer', 'Stroke', 'Alzheimer\'s Disease'
    ];
    
    const relationships = ['Father', 'Mother', 'Sibling', 'Grandparent'];
    
    const history: any[] = [];
    
    // 50% chance de tener historia familiar
    if (Math.random() < 0.5) {
      const numConditions = Math.floor(Math.random() * 3) + 1;
      
      for (let i = 0; i < numConditions; i++) {
        history.push({
          relationship: this.randomFromArray(relationships),
          condition: this.randomFromArray(conditions),
          ageAtDiagnosis: 40 + Math.floor(Math.random() * 30)
        });
      }
    }
    
    return history;
  }
  
  private generateSocialHistory(age: number) {
    return {
      smokingStatus: this.randomFromArray(['never', 'never', 'former', 'current']),
      alcoholUse: this.randomFromArray(['never', 'occasional', 'moderate']),
      exerciseFrequency: this.randomFromArray(['sedentary', 'light', 'moderate', 'active']),
      occupation: age < 65 ? faker.name.jobTitle() : 'Retired',
      maritalStatus: this.randomFromArray(['single', 'married', 'married', 'divorced'])
    };
  }
  
  private generateVitals(chronicConditions: any[]) {
    const hasHypertension = chronicConditions.some(c => c.icd10Code === 'I10');
    
    return {
      date: this.generateLastVisitDate(),
      bloodPressureSystolic: hasHypertension 
        ? 130 + Math.floor(Math.random() * 25)
        : 115 + Math.floor(Math.random() * 15),
      bloodPressureDiastolic: hasHypertension
        ? 80 + Math.floor(Math.random() * 15)
        : 70 + Math.floor(Math.random() * 15),
      heartRate: 65 + Math.floor(Math.random() * 25),
      temperature: 36.5 + Math.random() * 0.8,
      respiratoryRate: 14 + Math.floor(Math.random() * 6),
      oxygenSaturation: 96 + Math.floor(Math.random() * 4)
    };
  }
  
  private generateInsurance(isMexico: boolean, age: number) {
    const insurance: any[] = [];
    
    if (isMexico) {
      const providers = ['IMSS', 'ISSSTE', 'INSABI', 'AXA Seguros', 'GNP'];
      
      // 85% tiene seguro en México
      if (Math.random() < 0.85) {
        insurance.push({
          provider: this.randomFromArray(providers),
          policyNumber: faker.datatype.number({ min: 1000000000, max: 9999999999 }).toString(),
          effectiveDate: this.generatePastDate(5),
          expirationDate: this.generateFutureDate(2)
        });
      }
    } else {
      // USA
      let provider: string;
      
      if (age >= 65) {
        provider = 'Medicare';
      } else if (Math.random() < 0.3) {
        provider = 'Medi-Cal';
      } else {
        provider = this.randomFromArray([
          'Blue Cross Blue Shield',
          'Health Net',
          'Molina Healthcare',
          'United Healthcare'
        ]);
      }
      
      insurance.push({
        provider,
        policyNumber: faker.datatype.string(12).toUpperCase(),
        groupNumber: faker.datatype.string(8).toUpperCase(),
        effectiveDate: this.generatePastDate(3),
        expirationDate: this.generateFutureDate(1),
        copay: Math.random() < 0.7 ? [10, 15, 20, 25][Math.floor(Math.random() * 4)] : undefined
      });
    }
    
    return insurance;
  }
  
  private generateEmergencyContact(isHispanic: boolean) {
    const relationships = ['Spouse', 'Parent', 'Sibling', 'Child', 'Friend'];
    
    return {
      name: isHispanic 
        ? `${this.randomFromArray(this.hispanicFirstNamesFemale)} ${this.randomFromArray(this.hispanicLastNames)}`
        : faker.name.fullName(),
      relationship: this.randomFromArray(relationships),
      phone: this.generatePhone(isHispanic)
    };
  }
  
  private determinePrimaryLanguage(isMexico: boolean, isHispanic: boolean): 'es' | 'en' | 'es-en' {
    if (isMexico) return 'es';
    if (isHispanic) return Math.random() < 0.3 ? 'es-en' : 'en';
    return 'en';
  }
  
  private determineSecondaryLanguages(isMexico: boolean): string[] | undefined {
    if (isMexico && Math.random() < 0.4) {
      return ['English'];
    }
    if (!isMexico && Math.random() < 0.6) {
      return ['Spanish'];
    }
    return undefined;
  }
  
  private generateEmail(firstName: string, lastName: string): string {
    const domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com'];
    const cleanFirst = this.cleanForEmail(firstName);
    const cleanLast = this.cleanForEmail(lastName);
    const domain = this.randomFromArray(domains);
    
    return `${cleanFirst}.${cleanLast}${Math.floor(Math.random() * 999)}@${domain}`.toLowerCase();
  }
  
  private cleanForEmail(name: string): string {
    return name.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }
  
  private generatePhone(isMexico: boolean): string {
    if (isMexico) {
      return `+52 686 ${this.randomDigits(3)} ${this.randomDigits(4)}`;
    } else {
      return `+1 760 ${this.randomDigits(3)} ${this.randomDigits(4)}`;
    }
  }
  
  private randomDigits(length: number): string {
    return Array.from({ length }, () => Math.floor(Math.random() * 10)).join('');
  }
  
  private generateBloodType(): string {
    const types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
    const weights = [38, 7, 34, 6, 9, 2, 3, 1]; // Distribución aproximada
    
    return this.weightedRandom(types, weights);
  }
  
  private generateProviderName(isHispanic: boolean): string {
    const title = 'Dr.';
    const firstName = isHispanic
      ? this.randomFromArray(this.hispanicFirstNamesMale.concat(this.hispanicFirstNamesFemale))
      : faker.name.firstName();
    const lastName = isHispanic
      ? this.randomFromArray(this.hispanicLastNames)
      : faker.name.lastName();
    
    return `${title} ${firstName} ${lastName}`;
  }
  
  private getPreferredClinic(isMexico: boolean): string {
    if (isMexico) {
      return this.randomFromArray([
        'Hospital General de Mexicali',
        'Hospital de Especialidades IMSS',
        'Clínica del ISSSTE',
        'Hospital Almater'
      ]);
    } else {
      return this.randomFromArray([
        'Calexico Health Center',
        'Clinicas de Salud del Pueblo',
        'Imperial Valley Family Care'
      ]);
    }
  }
  
  private generateRegistrationDate(): Date {
    const yearsAgo = Math.floor(Math.random() * 10);
    const date = new Date();
    date.setFullYear(date.getFullYear() - yearsAgo);
    return date;
  }
  
  private generateLastVisitDate(): Date {
    const daysAgo = Math.floor(Math.random() * 180);
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);
    return date;
  }
  
  private generatePastDate(maxYearsAgo: number): Date {
    const yearsAgo = Math.random() * maxYearsAgo;
    const date = new Date();
    date.setFullYear(date.getFullYear() - yearsAgo);
    return date;
  }
  
  private generateFutureDate(maxYearsAhead: number): Date {
    const yearsAhead = Math.random() * maxYearsAhead;
    const date = new Date();
    date.setFullYear(date.getFullYear() + yearsAhead);
    return date;
  }
  
  private determineHighRisk(age: number, chronicConditions: any[], bmi: number): boolean {
    if (age > 75) return true;
    if (bmi > 35) return true;
    if (chronicConditions.length >= 3) return true;
    if (chronicConditions.some(c => c.icd10Code === 'E11.621')) return true; // Pie diabético
    return false;
  }
  
  private requiresInterpreter(isMexico: boolean, isHispanic: boolean): boolean {
    if (isMexico) return Math.random() < 0.15;
    if (isHispanic) return Math.random() < 0.25;
    return false;
  }
  
  private randomFromArray<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }
  
  private weightedRandom<T>(items: T[], weights: number[]): T {
    const total = weights.reduce((sum, w) => sum + w, 0);
    let random = Math.random() * total;
    
    for (let i = 0; i < items.length; i++) {
      random -= weights[i];
      if (random <= 0) {
        return items[i];
      }
    }
    
    return items[items.length - 1];
  }
}

// Uso del generador
const generator = new PatientMockDataGenerator();
const patients = generator.generatePatients(200);

// Exportar a JSON
import * as fs from 'fs';
fs.writeFileSync(
  'mock-patients-mexicali-calexico.json',
  JSON.stringify(patients, null, 2)
);

console.log(`✅ Generated ${patients.length} mock patients`);
console.log(`📊 Statistics:`);
console.log(`   - Mexicali residents: ${patients.filter(p => p.address.city === 'Mexicali').length}`);
console.log(`   - Calexico residents: ${patients.filter(p => p.address.city === 'Calexico').length}`);
console.log(`   - Hispanic/Latino: ${patients.filter(p => p.ethnicity === 'Hispanic or Latino').length}`);
console.log(`   - With chronic conditions: ${patients.filter(p => p.chronicConditions.length > 0).length}`);
console.log(`   - High risk patients: ${patients.filter(p => p.isHighRisk).length}`);
```

## Comandos de Ejecución

### Instalar dependencias
```bash
npm install @faker-js/faker uuid
npm install --save-dev @types/uuid
```

### Ejecutar generador
```bash
npx ts-node scripts/generate-mock-patients.ts
```

### Generar archivo SQL para inserción
```bash
npx ts-node scripts/generate-patient-sql.ts
```

## Validación de Datos

### Criterios de Validación
- ✅ Todos los campos requeridos están presentes
- ✅ Fechas son coherentes (fecha de nacimiento < fecha de diagnóstico < fecha actual)
- ✅ BMI calculado correctamente
- ✅ Distribución geográfica 60/40 Mexicali/Calexico
- ✅ Distribución de edad según especificaciones
- ✅ Prevalencia de condiciones crónicas realista
- ✅ Formatos de teléfono válidos para México/USA
- ✅ Códigos postales correctos
- ✅ Nombres culturalmente apropiados

## Archivos de Salida

### 1. JSON Principal
`data/mock/patients-200-mexicali-calexico.json`
- Contiene los 200 registros completos
- Formato: JSON array de objetos PatientMockData

### 2. CSV para Excel
`data/mock/patients-200-mexicali-calexico.csv`
- Versión plana para análisis en Excel
- Campos principales separados por comas

### 3. SQL Insert Statements
`data/mock/patients-insert.sql`
- Scripts SQL para inserción directa en base de datos
- Compatible con PostgreSQL/MySQL

### 4. Reporte Estadístico
`data/mock/patients-statistics.md`
- Resumen de distribuciones
- Gráficos de prevalencia
- Validaciones pasadas/fallidas

## Integración con Sistema

### Import en Backend (NestJS)
```typescript
import patientsData from './data/mock/patients-200-mexicali-calexico.json';

@Injectable()
export class PatientSeederService {
  async seedPatients() {
    for (const patientData of patientsData) {
      await this.patientRepository.create(patientData);
    }
  }
}
```

### API Endpoint de Testing
```typescript
@Controller('dev')
export class DevController {
  @Get('seed-patients')
  @UseGuards(DevGuard) // Solo en desarrollo
  async seedMockPatients() {
    const generator = new PatientMockDataGenerator();
    const patients = generator.generatePatients(200);
    
    await this.patientService.bulkCreate(patients);
    
    return {
      message: '200 mock patients created successfully',
      count: patients.length
    };
  }
}
```

## Consideraciones de Privacidad

⚠️ **IMPORTANTE**: Estos son datos MOCK/FICTICIOS para desarrollo y testing únicamente.

- ❌ NO usar datos reales de pacientes
- ❌ NO contiene información HIPAA
- ❌ NO usar en producción
- ✅ Solo para ambientes de desarrollo/staging
- ✅ Datos completamente ficticios
- ✅ Sin correspondencia con personas reales

## Mantenimiento

### Actualización de Datos
- Revisar prevalencias médicas anualmente
- Actualizar nombres comunes según censo
- Ajustar direcciones si hay cambios urbanos
- Actualizar proveedores de seguro activos

### Versiones
- **v1.0.0**: Generación inicial de 200 pacientes
- Futuras versiones pueden incluir:
  - Más condiciones específicas de podología
  - Historiales de citas y tratamientos
  - Imágenes médicas mock
  - Resultados de laboratorio

## Referencias

- **Datos demográficos**: INEGI (México), US Census Bureau
- **Prevalencias médicas**: 
  - CDC National Diabetes Statistics Report
  - AHA Heart Disease Statistics
  - NIH Chronic Disease Prevalence
- **Nombres**: Registros civiles de BC y CA
- **Geografía**: OpenStreetMap, Google Maps API

## Soporte

Para preguntas o mejoras en la generación de datos mock:
- Crear issue en GitHub con etiqueta `dev-tools`
- Contactar al equipo de desarrollo
- Revisar documentación de faker.js

---

**Última actualización**: 2026-01-01
**Mantenedor**: Dev Team - Podiskin
**Licencia**: Internal Use Only
