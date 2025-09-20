# Notification System Integration Guide

## Overview

The CryptoConnect application now has a unified notification system that automatically shows both:
1. **Toast notifications** (temporary messages at the bottom of the screen)
2. **Header notifications** (persistent notifications in the notification dropdown)

## How It Works

When you login, register, submit forms, or perform any actions, the system will:
- Show a toast notification immediately (temporary, disappears after a few seconds)
- Add the same notification to the header notification dropdown (persistent until manually cleared)

## Key Components

### 1. NotificationProvider
- Wraps the entire application
- Manages notification state globally
- Located in `/src/hooks/use-notifications.tsx`

### 2. Header Notification Dropdown
- Shows all notifications with timestamps
- Allows individual clearing (X button on hover)
- Allows clearing all notifications ("Clear All" button)
- Color-coded by notification type:
  - 🟢 Green: Success notifications
  - 🔵 Blue: Income notifications  
  - 🔴 Red: Error notifications
  - ⚫ Gray: Info notifications

### 3. Toast Integration
- All notifications automatically appear as toasts too
- Error notifications show as red "destructive" toasts
- Success/info notifications show as regular toasts

## Usage Examples

### In Authentication (Already Implemented)
```typescript
// Login success
showToastAndNotification(
  "Login successful",
  `Welcome back, ${user.firstName}!`,
  "success"
);

// Login error
showToastAndNotification(
  "Login failed", 
  error.message,
  "error"
);
```

### In Other Components
```typescript
import { useNotifications } from "@/hooks/use-notifications";

export function MyComponent() {
  const { showToastAndNotification } = useNotifications();

  const handleSubmit = async () => {
    try {
      await submitData();
      showToastAndNotification(
        "Form Submitted",
        "Your data has been saved successfully",
        "success"
      );
    } catch (error) {
      showToastAndNotification(
        "Submission Failed",
        error.message,
        "error"
      );
    }
  };

  return <button onClick={handleSubmit}>Submit</button>;
}
```

### For Income Notifications
```typescript
showToastAndNotification(
  "Monthly Income Received",
  `You received AED ${amount} from your properties`,
  "success"
);
```

## Notification Types

- **success**: Green color, for successful operations
- **error**: Red color, for errors and failures  
- **info**: Gray color, for general information
- **income**: Blue color, for financial transactions

## Features

### User Controls
- **Individual Clear**: Hover over notification → click X button
- **Clear All**: Click "Clear All" button in header
- **Demo Notifications**: Click "Add Demo Notification" when list is empty (for testing)

### Visual Indicators
- **Unread Badge**: Red dot on bell icon when notifications exist
- **Unread Count**: Shows number of unread notifications
- **Color Coding**: Different colored dots for different types
- **Timestamps**: Shows "Just now" for new notifications

### Responsive Design
- Works on all screen sizes
- Dropdown positioned correctly
- Mobile-friendly touch interactions

## Benefits

1. **Unified Experience**: Users see notifications in two places - immediate toast + persistent header
2. **No Lost Messages**: Important notifications don't disappear forever
3. **User Control**: Users can clear notifications when ready
4. **Automatic Integration**: All existing toast usage automatically gets header notifications too
5. **Type Safety**: Full TypeScript support with proper interfaces

## Current Integration Status

✅ **Login/Register**: Both toast and header notifications
✅ **Logout**: Both toast and header notifications  
✅ **KYC Submission**: Both toast and header notifications
🔄 **Future**: Property submissions, transactions, income notifications

## Next Steps

To add notifications to other parts of the app:
1. Import `useNotifications` hook
2. Use `showToastAndNotification()` instead of regular `toast()`
3. Choose appropriate notification type (success, error, info, income)
4. Test both toast appearance and header notification addition

The system is now ready to capture all user actions and provide a comprehensive notification experience!