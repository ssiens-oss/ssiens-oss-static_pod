/**
 * Toast Container Component
 * Container for displaying toast notifications
 */

import Toast from './Toast';
import useStore from '../store';

const ToastContainer = () => {
  const notifications = useStore((state) => state.notifications);
  const removeNotification = useStore((state) => state.removeNotification);

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          id={notification.id}
          type={notification.type}
          message={notification.message}
          onClose={removeNotification}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
