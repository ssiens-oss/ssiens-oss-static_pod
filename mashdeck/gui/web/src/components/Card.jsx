/**
 * Card Component
 * Reusable card container with glass effect
 */

import { clsx } from 'clsx';

const Card = ({
  children,
  className = '',
  variant = 'default',
  padding = 'md',
  hover = false,
  onClick,
  ...props
}) => {
  const baseStyles = 'rounded-xl backdrop-blur-sm transition-all duration-200';

  const variants = {
    default: 'bg-secondary/50 border border-white/10',
    glass: 'glass',
    solid: 'bg-secondary border border-white/5',
    gradient: 'bg-gradient-to-br from-accent/20 to-transparent border border-accent/20'
  };

  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8'
  };

  const hoverStyles = hover
    ? 'cursor-pointer hover:border-accent/50 hover:shadow-lg hover:shadow-accent/10 hover:-translate-y-1'
    : '';

  return (
    <div
      className={clsx(
        baseStyles,
        variants[variant],
        paddings[padding],
        hoverStyles,
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
