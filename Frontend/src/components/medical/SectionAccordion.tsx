import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, Circle } from 'lucide-react';
import { clsx } from 'clsx';
import type { FormSection, FormFieldConfig } from '../../types/medical';
import { useFormContext } from 'react-hook-form';
import FormField, { CurrencyField, PhoneField } from './fields/FormField';

interface SectionAccordionProps {
  section: FormSection;
  isOpen?: boolean;
  onToggle?: (isOpen: boolean) => void;
  showProgress?: boolean;
  progress?: number;
}

const SectionAccordion: React.FC<SectionAccordionProps> = ({
  section,
  isOpen: controlledIsOpen,
  onToggle,
  showProgress = false,
  progress = 0,
}) => {
  const [internalIsOpen, setInternalIsOpen] = useState(controlledIsOpen ?? true);
  const isOpen = controlledIsOpen ?? internalIsOpen;
  
  const handleToggle = () => {
    const newValue = !isOpen;
    if (controlledIsOpen === undefined) {
      setInternalIsOpen(newValue);
    }
    onToggle?.(newValue);
  };

  // Contar campos completados
  const { watch } = useFormContext();
  const formData = watch();
  
  const calculateProgress = () => {
    let completed = 0;
    let total = 0;
    
    section.fields.forEach(field => {
      // Verificar condición dependsOn
      if (field.dependsOn) {
        const depValue = getNestedValue(formData, field.dependsOn.field);
        if (depValue !== field.dependsOn.value) return;
      }
      
      total += 1;
      const fieldValue = getNestedValue(formData, field.name);
      
      if (fieldValue !== undefined && fieldValue !== '' && fieldValue !== null) {
        if (Array.isArray(fieldValue) && fieldValue.length === 0) {
          // Array vacío no cuenta como completado
        } else {
          completed += 1;
        }
      }
    });
    
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  const sectionProgress = showProgress ? calculateProgress() : progress;
  const isComplete = sectionProgress === 100;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
      {/* Header del acordeón */}
      <button
        type="button"
        onClick={handleToggle}
        className={clsx(
          'w-full px-4 py-3 flex items-center justify-between transition-colors',
          'hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-teal-500'
        )}
      >
        <div className="flex items-center gap-3">
          {/* Icono de estado */}
          {isComplete ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : sectionProgress > 0 ? (
            <div className="relative">
              <Circle className="w-5 h-5 text-yellow-500" />
              <div 
                className="absolute inset-0 text-yellow-500 overflow-hidden"
                style={{ clipPath: `inset(0 ${100 - sectionProgress}% 0 0)` }}
              >
                <Circle className="w-5 h-5" />
              </div>
            </div>
          ) : (
            <Circle className="w-5 h-5 text-gray-300" />
          )}
          
          <div className="text-left">
            <h3 className="text-sm font-semibold text-gray-800">
              {section.title}
            </h3>
            {section.description && (
              <p className="text-xs text-gray-500 mt-0.5">
                {section.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Barra de progreso */}
          {showProgress && (
            <div className="w-24 hidden sm:block">
              <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={clsx(
                    'h-full rounded-full transition-all duration-300',
                    isComplete ? 'bg-green-500' : 'bg-teal-500'
                  )}
                  style={{ width: `${sectionProgress}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 mt-0.5 block text-center">
                {sectionProgress}%
              </span>
            </div>
          )}
          
          {/* Chevron */}
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* Contenido del acordeón */}
      {isOpen && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <div className="pt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {section.fields.map((field) => (
              <FieldRenderer key={field.name} field={field} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Componente para renderizar campos según su tipo
const FieldRenderer: React.FC<{ field: FormFieldConfig }> = ({ field }) => {
  // Special case for array fields - they need a different renderer
  if (field.type === 'array') {
    return <ArrayFieldRenderer field={field} />;
  }

  // Select the appropriate field component
  if (field.type === 'currency') {
    return <CurrencyField {...field} />;
  }
  
  if (field.type === 'phone') {
    return <PhoneField {...field} />;
  }

  return <FormField {...field} />;
};

// Renderer especial para campos tipo array (listas dinámicas)
interface ArrayFieldRendererProps {
  field: FormFieldConfig;
}

const ArrayFieldRenderer: React.FC<ArrayFieldRendererProps> = ({ field }) => {
  const { watch, setValue } = useFormContext();
  const items = watch(field.name) || [];
  
  const addItem = () => {
    const currentItems = items || [];
    const newItem = createEmptyItem(field.name);
    setValue(field.name, [...currentItems, newItem]);
  };
  
  const removeItem = (index: number) => {
    const currentItems = [...items];
    currentItems.splice(index, 1);
    setValue(field.name, currentItems);
  };

  return (
    <div className="col-span-full">
      <label className="flex items-center gap-1 mb-2 text-sm font-medium text-gray-700">
        {field.label}
        {field.helpText && (
          <span className="text-gray-400 text-xs ml-1">({field.helpText})</span>
        )}
      </label>
      
      {items.map((_: any, index: number) => (
        <ArrayItemRenderer 
          key={index} 
          field={field} 
          index={index} 
          onRemove={() => removeItem(index)}
        />
      ))}
      
      <button
        type="button"
        onClick={addItem}
        className="mt-2 px-3 py-1.5 text-sm text-teal-600 bg-teal-50 border border-teal-200 rounded-md hover:bg-teal-100 transition-colors"
      >
        + Agregar {field.label.slice(0, -1) || 'Elemento'}
      </button>
    </div>
  );
};

// Renderer para cada elemento del array
interface ArrayItemRendererProps {
  field: FormFieldConfig;
  index: number;
  onRemove: () => void;
}

const ArrayItemRenderer: React.FC<ArrayItemRendererProps> = ({ field, index, onRemove }) => {
  const basePath = `${field.name}[${index}]`;
  
  return (
    <div className="p-3 mb-2 bg-gray-50 border border-gray-200 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-medium text-gray-500">
          Elemento {index + 1}
        </span>
        <button
          type="button"
          onClick={onRemove}
          className="text-red-500 hover:text-red-700 text-xs"
        >
          Eliminar
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        {/* Renderizar campos específicos según el tipo de array */}
        {field.name.includes('alergias') && (
          <>
            <FormField
              name={`${basePath}.tipo_alergeno`}
              label="Tipo"
              type="select"
              options={[
                { value: '', label: 'Seleccionar...' },
                { value: 'Medicamento', label: 'Medicamento' },
                { value: 'Alimento', label: 'Alimento' },
                { value: 'Ambiental', label: 'Ambiental' },
                { value: 'Material', label: 'Material' },
                { value: 'Otro', label: 'Otro' },
              ]}
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.nombre_alergeno`}
              label="Alérgeno"
              type="text"
              placeholder="Nombre del alérgeno"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.reaccion`}
              label="Reacción"
              type="text"
              placeholder="Reacción experimentada"
            />
            <FormField
              name={`${basePath}.severidad`}
              label="Severidad"
              type="select"
              options={[
                { value: '', label: 'Seleccionar...' },
                { value: 'Leve', label: 'Leve' },
                { value: 'Moderada', label: 'Moderada' },
                { value: 'Grave', label: 'Grave' },
                { value: 'Mortal', label: 'Mortal' },
              ]}
            />
          </>
        )}
        
        {field.name.includes('heredofamiliares') && (
          <>
            <FormField
              name={`${basePath}.enfermedad`}
              label="Enfermedad"
              type="text"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.parentesco`}
              label="Parentesco"
              type="text"
              validation={{ required: true }}
            />
          </>
        )}
        
        {field.name.includes('patologicos') && (
          <>
            <FormField
              name={`${basePath}.enfermedad`}
              label="Enfermedad"
              type="text"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.esta_controlado`}
              label="¿Está controlado?"
              type="boolean"
            />
          </>
        )}
        
        {field.name.includes('quirurgicos') && (
          <>
            <FormField
              name={`${basePath}.tipo_cirugia`}
              label="Tipo de Cirugía"
              type="text"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.fecha`}
              label="Fecha"
              type="date"
            />
          </>
        )}
        
        {field.name.includes('traumaticos') && (
          <>
            <FormField
              name={`${basePath}.tipo_traumatismo`}
              label="Tipo de Traumatismo"
              type="text"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.fecha`}
              label="Fecha"
              type="date"
            />
          </>
        )}
        
        {field.name.includes('diagnosticos') && (
          <>
            <FormField
              name={`${basePath}.tipo`}
              label="Tipo"
              type="select"
              options={[
                { value: '', label: 'Seleccionar...' },
                { value: 'Presuntivo', label: 'Presuntivo' },
                { value: 'Definitivo', label: 'Definitivo' },
                { value: 'Diferencial', label: 'Diferencial' },
              ]}
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.descripcion`}
              label="Descripción"
              type="textarea"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.cie10_catalogo`}
              label="CIE-10"
              type="select"
              options={[
                { value: '', label: 'Seleccionar código...' },
                { value: 'E10.9', label: 'E10.9 - Diabetes mellitus tipo 1' },
                { value: 'E11.9', label: 'E11.9 - Diabetes mellitus tipo 2' },
                { value: 'B35.1', label: 'B35.1 - Onicomicosis' },
                { value: 'B35.3', label: 'B35.3 - Pie de atleta' },
                { value: 'M20.1', label: 'M20.1 - Hallux valgus' },
                { value: 'M72.2', label: 'M72.2 - Fascitis plantar' },
                { value: 'M77.3', label: 'M77.3 - Espolón calcáneo' },
                { value: 'L60.0', label: 'L60.0 - Uña incarnada' },
                { value: 'L84', label: 'L84 - Callo y callosidad' },
                { value: 'B07', label: 'B07 - Verugas' },
              ]}
            />
          </>
        )}
        
        {field.name.includes('plan_tratamiento') && (
          <>
            <FormField
              name={`${basePath}.servicio`}
              label="Servicio/Tratamiento"
              type="select"
              options={[
                { value: '', label: 'Seleccionar...' },
                { value: 'CONS', label: 'CONS - Consulta' },
                { value: 'QUIR', label: 'QUIR - Quiropodia' },
                { value: 'ONIC', label: 'ONIC - Onicomicosis' },
                { value: 'VERU', label: 'VERU - Verrugas' },
                { value: 'CALO', label: 'CALO - Callos' },
                { value: 'ORTO', label: 'ORTO - Ortesis' },
                { value: 'PLANT', label: 'PLANT - Plantillas' },
              ]}
              validation={{ required: true }}
            />
            <CurrencyField
              name={`${basePath}.precio_aplicado`}
              label="Precio"
              type="currency"
            />
          </>
        )}
        
        {field.name.includes('evolucion') && (
          <>
            <FormField
              name={`${basePath}.fase`}
              label="Fase"
              type="number"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.fecha_evaluacion`}
              label="Fecha"
              type="date"
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.resultado`}
              label="Resultado"
              type="select"
              options={[
                { value: '', label: 'Seleccionar...' },
                { value: 'Mejoría', label: 'Mejoría' },
                { value: 'Sin cambios', label: 'Sin cambios' },
                { value: 'Empeoramiento', label: 'Empeoramiento' },
              ]}
              validation={{ required: true }}
            />
            <FormField
              name={`${basePath}.descripcion`}
              label="Descripción"
              type="textarea"
              gridCols={12}
              validation={{ required: true }}
            />
          </>
        )}
        
        {/* Generic fallback */}
        {!field.name.includes('alergias') && 
         !field.name.includes('heredofamiliares') && 
         !field.name.includes('patologicos') &&
         !field.name.includes('quirurgicos') &&
         !field.name.includes('traumaticos') &&
         !field.name.includes('diagnosticos') &&
         !field.name.includes('plan_tratamiento') &&
         !field.name.includes('evolucion') && (
          <FormField
            name={`${basePath}.descripcion`}
            label="Descripción"
            type="textarea"
            gridCols={12}
          />
        )}
      </div>
    </div>
  );
};

// Utilidad para crear items vacíos según el tipo de array
const createEmptyItem = (arrayPath: string): any => {
  if (arrayPath.includes('alergias')) {
    return {
      id: crypto.randomUUID(),
      tipo_alergeno: '',
      nombre_alergeno: '',
      reaccion: '',
      severidad: '',
    };
  }
  
  if (arrayPath.includes('heredofamiliares')) {
    return { id: crypto.randomUUID(), enfermedad: '', parentesco: '' };
  }
  
  if (arrayPath.includes('patologicos')) {
    return { id: crypto.randomUUID(), enfermedad: '', esta_controlado: false };
  }
  
  if (arrayPath.includes('quirurgicos')) {
    return { id: crypto.randomUUID(), tipo_cirugia: '', fecha: '' };
  }
  
  if (arrayPath.includes('traumaticos')) {
    return { id: crypto.randomUUID(), tipo_traumatismo: '', fecha: '' };
  }
  
  if (arrayPath.includes('diagnosticos')) {
    return { id: crypto.randomUUID(), tipo: '', descripcion: '', cie10_catalogo: '' };
  }
  
  if (arrayPath.includes('plan_tratamiento')) {
    return { id: crypto.randomUUID(), servicio: '', precio_aplicado: 0 };
  }
  
  if (arrayPath.includes('evolucion')) {
    return { id: crypto.randomUUID(), fase: 0, fecha_evaluacion: '', resultado: '', descripcion: '' };
  }
  
  return { id: crypto.randomUUID() };
};

// Utilidad para obtener valor anidado
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((acc, part) => {
    // Manejar arrays como "nombre[0].campo"
    const arrayMatch = part.match(/(\w+)\[(\d+)\]/);
    if (arrayMatch) {
      const [, arrayName, index] = arrayMatch;
      return acc?.[arrayName]?.[parseInt(index)];
    }
    return acc && acc[part];
  }, obj);
}

export default SectionAccordion;
