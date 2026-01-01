/**
 * Input Component
 * Reusable input field with label and validation
 */

import { clsx } from 'clsx';

const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  disabled = false,
  required = false,
  className = '',
  icon,
  ...props
}) => {
  const baseStyles = 'w-full px-4 py-2.5 rounded-lg bg-secondary border border-white/10 text-white placeholder-gray-500 transition-all duration-200 focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
          {required && <span className="text-accent ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}

        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={clsx(
            baseStyles,
            icon && 'pl-10',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
          )}
          {...props}
        />
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};

export default Input;
