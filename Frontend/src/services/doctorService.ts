/**
 * Doctor/Podólogo Service
 * Servicio para gestionar podólogos desde el backend
 */

import axios from 'axios';
import api from './api';

// Backend response interface
interface PodologoBackend {
    id: number;
    nombre_completo: string;
    cedula_profesional: string;
    especialidad: string | null;
    telefono: string;
    email: string | null;
    activo: boolean;
}

// Frontend Doctor interface (matches App.tsx expectations)
export interface Doctor {
    id: string;
    name: string;
    color: string;
    workingHours?: {
        start: number;
        end: number;
    };
}

// Color palette for doctors
const DOCTOR_COLORS = [
    'bg-blue-100 text-blue-700 border-blue-200',
    'bg-emerald-100 text-emerald-700 border-emerald-200',
    'bg-purple-100 text-purple-700 border-purple-200',
    'bg-pink-100 text-pink-700 border-pink-200',
    'bg-orange-100 text-orange-700 border-orange-200',
    'bg-teal-100 text-teal-700 border-teal-200',
    'bg-indigo-100 text-indigo-700 border-indigo-200',
    'bg-rose-100 text-rose-700 border-rose-200',
];

/**
 * Transform backend podologo to frontend doctor format
 */
function transformPodologoToDoctor(podologo: PodologoBackend, index: number): Doctor {
    return {
        id: String(podologo.id),
        name: podologo.nombre_completo,
        color: DOCTOR_COLORS[index % DOCTOR_COLORS.length],
        workingHours: {
            start: 9,
            end: 18
        }
    };
}

/**
 * Get all available doctors/podólogos
 */
export async function getDoctors(): Promise<Doctor[]> {
    try {
        const response = await api.get<PodologoBackend[]>('/api/podologos/disponibles');
        
        // Transform backend data to frontend format
        const doctors = response.data.map((podologo, index) => 
            transformPodologoToDoctor(podologo, index)
        );

        console.log(`✅ Loaded ${doctors.length} doctors from API`);
        return doctors;
    } catch (error) {
        console.error('❌ Error loading doctors:', error);
        
        if (axios.isAxiosError(error)) {
            if (error.response?.status === 401) {
                throw new Error('No autorizado. Por favor inicia sesión.');
            } else if (error.response?.status === 404) {
                throw new Error('Endpoint de podólogos no encontrado.');
            }
        }
        
        throw new Error('Error al cargar la lista de podólogos. Por favor intenta de nuevo.');
    }
}

/**
 * Get all doctors including inactive ones
 */
export async function getAllDoctors(): Promise<Doctor[]> {
    try {
        const response = await api.get<PodologoBackend[]>('/api/podologos', {
            params: { activo_only: false }
        });
        
        const doctors = response.data.map((podologo, index) => 
            transformPodologoToDoctor(podologo, index)
        );

        return doctors;
    } catch (error) {
        console.error('Error loading all doctors:', error);
        throw error;
    }
}

export default {
    getDoctors,
    getAllDoctors,
};
