import React, { type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { useFormContext, useFormState } from 'react-hook-form';
import type { FormFieldConfig, SelectOption } from '../../types/medical';
import HelpTooltip from '../HelpTooltip';

// ============================================================================
// INTERFACES
// ============================================================================

interface BaseFieldProps extends Omit<FormFieldConfig, 'name'> {
  name: string;
  className?: string;
  onChange?: (value: any) => void;
  onBlur?: () => void;
}

interface TextFieldProps extends BaseFieldProps {
  type: 'text' | 'email' | 'phone' | 'password';
}

interface NumberFieldProps extends BaseFieldProps {
  type: 'number';
}

interface DateFieldProps extends BaseFieldProps {
  type: 'date' | 'datetime';
}

interface SelectFieldProps extends BaseFieldProps {
  type: 'select' | 'multiselect';
}

interface TextareaFieldProps extends BaseFieldProps {
  type: 'textarea';
}

interface RadioFieldProps extends BaseFieldProps {
  type: 'radio';
}

interface CheckboxFieldProps extends BaseFieldProps {
  type: 'boolean' | 'checkbox';
}

interface ArrayFieldProps extends BaseFieldProps {
  type: 'array';
}

type FormFieldProps = TextFieldProps | NumberFieldProps | DateFieldProps | 
                      SelectFieldProps | TextareaFieldProps | RadioFieldProps | 
                      CheckboxFieldProps | ArrayFieldProps;

// ============================================================================
// COMPONENTE PRINCIPAL
// ============================================================================

const FormField = forwardRef<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement, FormFieldProps>(
  ({ 
    name, 
    label, 
    type, 
    placeholder, 
    helpText, 
    options, 
    validation, 
    dependsOn, 
    gridCols = 12,
    className,
    onChange,
    onBlur,
  }, ref) => {
    const { register, watch, setValue, formState: { errors } } = useFormContext();
    const fieldError = errors[name]?.message as string | undefined;
    const isRequired = validation?.required;
    
    // Verificar condición dependsOn
    const dependentValue = dependsOn ? watch(dependsOn.field) : undefined;
    const isVisible = !dependsOn || dependentValue === dependsOn.value;
    
    if (!isVisible) {
      return null;
    }

    const baseInputClasses = clsx(
      'w-full px-3 py-2 text-sm border rounded-lg transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
      'placeholder:text-gray-400',
      'bg-white',
      fieldError 
        ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' 
        : 'border-gray-200 hover:border-gray-300',
      'disabled:bg-gray-100 disabled:cursor-not-allowed'
    );

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      let value: any = e.target.value;
      
      if (type === 'number') {
        value = e.target.value ? parseFloat(e.target.value) : undefined;
      } else if (type === 'boolean' || type === 'checkbox') {
        value = e.target.checked;
      }
      
      setValue(name, value, { shouldValidate: true });
      onChange?.(value);
    };

    return (
      <div className={clsx('flex flex-col', gridCols < 12 && `col-span-${gridCols}`, className)}>
        <label className="flex items-center gap-1 mb-1 text-sm font-medium text-gray-700">
          {label}
          {isRequired && <span className="text-red-500">*</span>}
          {helpText && <HelpTooltip text={helpText} />}
        </label>
        
        {type === 'text' || type === 'email' || type === 'phone' || type === 'password' ? (
          <input
            ref={ref as React.RefObject<HTMLInputElement>}
            type={type}
            placeholder={placeholder}
            className={baseInputClasses}
            {...register(name, {
              required: isRequired ? validation?.message || `${label} es obligatorio` : false,
              min: validation?.min,
              max: validation?.max,
              minLength: validation?.minLength,
              maxLength: validation?.maxLength,
              pattern: validation?.pattern ? new RegExp(validation.pattern) : undefined,
              onChange: handleChange,
              onBlur,
            })}
          />
        ) : type === 'number' ? (
          <input
            ref={ref as React.RefObject<HTMLInputElement>}
            type="number"
            placeholder={placeholder}
            step="any"
            className={baseInputClasses}
            {...register(name, {
              required: isRequired ? validation?.message || `${label} es obligatorio` : false,
              min: validation?.min,
              max: validation?.max,
              valueAsNumber: true,
              onChange: handleChange,
              onBlur,
            })}
          />
        ) : type === 'date' || type === 'datetime' ? (
          <input
            ref={ref as React.RefObject<HTMLInputElement>}
            type={type === 'datetime' ? 'datetime-local' : 'date'}
            placeholder={placeholder}
            className={baseInputClasses}
            {...register(name, {
              required: isRequired ? validation?.message || `${label} es obligatorio` : false,
              onChange: handleChange,
              onBlur,
            })}
          />
        ) : type === 'select' ? (
          <select
            ref={ref as React.RefObject<HTMLSelectElement>}
            className={baseInputClasses}
            {...register(name, {
              required: isRequired ? validation?.message || `${label} es obligatorio` : false,
              onChange: handleChange,
              onBlur,
            })}
          >
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : type === 'textarea' ? (
          <textarea
            ref={ref as React.RefObject<HTMLTextAreaElement>}
            placeholder={placeholder}
            rows={3}
            className={clsx(baseInputClasses, 'resize-none')}
            {...register(name, {
              required: isRequired ? validation?.message || `${label} es obligatorio` : false,
              minLength: validation?.minLength,
              maxLength: validation?.maxLength,
              onChange: handleChange,
              onBlur,
            })}
          />
        ) : type === 'radio' ? (
          <div className="flex flex-wrap gap-3 mt-1">
            {options?.map((option) => (
              <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value={option.value}
                  className="w-4 h-4 text-teal-600 border-gray-300 focus:ring-teal-500"
                  {...register(name, {
                    required: isRequired ? validation?.message || `${label} es obligatorio` : false,
                    onChange: handleChange,
                  })}
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        ) : type === 'boolean' || type === 'checkbox' ? (
          <div className="flex items-center gap-2 mt-1">
            <input
              ref={ref as React.RefObject<HTMLInputElement>}
              type="checkbox"
              className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
              {...register(name, {
                onChange: (e) => {
                  setValue(name, e.target.checked, { shouldValidate: true });
                  onChange?.(e.target.checked);
                },
              })}
            />
            <span className="text-sm text-gray-600">{placeholder || 'Sí'}</span>
          </div>
        ) : null}
        
        {fieldError && (
          <p className="mt-1 text-xs text-red-500">{fieldError}</p>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';

// ============================================================================
// SUBCOMPONENTES PARA TIPOS ESPECIALES
// ============================================================================

// Currency Field
interface CurrencyFieldProps extends Omit<BaseFieldProps, 'type'> {
  type: 'currency';
  currency?: string;
}

export const CurrencyField = forwardRef<HTMLInputElement, CurrencyFieldProps>(
  ({ name, label, placeholder, helpText, validation, gridCols, currency = 'MXN', className }, ref) => {
    const { register, formState: { errors } } = useFormContext();
    const fieldError = errors[name]?.message as string | undefined;
    const isRequired = validation?.required;

    return (
      <div className={clsx('flex flex-col', className)}>
        <label className="flex items-center gap-1 mb-1 text-sm font-medium text-gray-700">
          {label}
          {isRequired && <span className="text-red-500">*</span>}
          {helpText && <HelpTooltip text={helpText} />}
        </label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
            {currency === 'MXN' ? '$' : currency}
          </span>
          <input
            ref={ref}
            type="number"
            placeholder={placeholder}
            step="0.01"
            className={clsx(
              'w-full pl-7 pr-3 py-2 text-sm border rounded-lg transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
              'placeholder:text-gray-400 bg-white',
              fieldError 
                ? 'border-red-300 bg-red-50 focus:ring-red-500' 
                : 'border-gray-200 hover:border-gray-300'
            )}
            {...register(name, {
              required: isRequired ? validation?.message : false,
              min: validation?.min,
              max: validation?.max,
              valueAsNumber: true,
            })}
          />
        </div>
        {fieldError && <p className="mt-1 text-xs text-red-500">{fieldError}</p>}
      </div>
    );
  }
);

CurrencyField.displayName = 'CurrencyField';

// Phone Field con formato
interface PhoneFieldProps extends Omit<BaseFieldProps, 'type'> {
  type: 'phone';
}

export const PhoneField = forwardRef<HTMLInputElement, PhoneFieldProps>(
  ({ name, label, placeholder, helpText, validation, gridCols, className }, ref) => {
    const { register, formState: { errors } } = useFormContext();
    const fieldError = errors[name]?.message as string | undefined;
    const isRequired = validation?.required;

    const formatPhone = (value: string) => {
      const cleaned = value.replace(/\D/g, '');
      if (cleaned.length <= 10) {
        return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
      }
      return cleaned.slice(0, 10).replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
    };

    return (
      <div className={clsx('flex flex-col', className)}>
        <label className="flex items-center gap-1 mb-1 text-sm font-medium text-gray-700">
          {label}
          {isRequired && <span className="text-red-500">*</span>}
          {helpText && <HelpTooltip text={helpText} />}
        </label>
        <input
          ref={ref}
          type="tel"
          placeholder={placeholder || '123-456-7890'}
          maxLength={12}
          className={clsx(
            'w-full px-3 py-2 text-sm border rounded-lg transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder:text-gray-400 bg-white',
            fieldError 
              ? 'border-red-300 bg-red-50 focus:ring-red-500' 
              : 'border-gray-200 hover:border-gray-300'
          )}
          {...register(name, {
            required: isRequired ? validation?.message : false,
            pattern: {
              value: /^[0-9]{3}-[0-9]{3}-[0-9]{4}$/,
              message: 'Formato: 123-456-7890',
            },
            onChange: (e) => {
              e.target.value = formatPhone(e.target.value);
            },
          })}
        />
        {fieldError && <p className="mt-1 text-xs text-red-500">{fieldError}</p>}
      </div>
    );
  }
);

PhoneField.displayName = 'PhoneField';

// ============================================================================
// EXPORT
// ============================================================================

export default FormField;
