import React, { createContext, useContext, useState } from 'react';
import { toast } from './use-toast';

export interface Notification {
  id: number;
  title: string;
  message: string;
  time: string;
  type: 'success' | 'income' | 'info' | 'error';
  unread: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'time' | 'unread'>) => void;
  clearNotification: (id: number) => void;
  clearAllNotifications: () => void;
  markAsRead: (id: number) => void;
  showToastAndNotification: (title: string, message: string, type?: 'success' | 'error' | 'info') => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (notification: Omit<Notification, 'id' | 'time' | 'unread'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now(),
      time: 'Just now',
      unread: true,
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const clearNotification = (id: number) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const markAsRead = (id: number) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id
          ? { ...notification, unread: false }
          : notification
      )
    );
  };

  const showToastAndNotification = (title: string, message: string, type: 'success' | 'error' | 'info' = 'info') => {
    // Show toast notification
    toast({
      title,
      description: message,
      variant: type === 'error' ? 'destructive' : 'default',
    });

    // Add to header notifications (convert error to info for cleaner notification display)
    const notificationType: 'success' | 'income' | 'info' | 'error' = 
      type === 'success' ? 'success' : 
      type === 'error' ? 'error' :
      'info';

    addNotification({
      title,
      message,
      type: notificationType,
    });
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      clearNotification,
      clearAllNotifications,
      markAsRead,
      showToastAndNotification,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};