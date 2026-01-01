/**
 * ProgressBar Component
 * Progress indicator bar
 */

import { clsx } from 'clsx';

const ProgressBar = ({
  progress = 0,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  className = ''
}) => {
  const variants = {
    primary: 'bg-accent',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500'
  };

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const percentage = Math.min(Math.max(progress * 100, 0), 100);

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex justify-between mb-1">
          <span className="text-sm text-gray-400">Progress</span>
          <span className="text-sm font-medium text-white">{percentage.toFixed(0)}%</span>
        </div>
      )}
      <div className={clsx('w-full bg-secondary/50 rounded-full overflow-hidden', sizes[size])}>
        <div
          className={clsx('h-full transition-all duration-500 ease-out', variants[variant])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
