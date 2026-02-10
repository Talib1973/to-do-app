'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../ui/Button';

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = () => {
    // Clear authentication data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    // Redirect to login page
    router.push('/login');
  };

  return (
    <Button
      onClick={handleLogout}
      variant="secondary"
    >
      Log Out
    </Button>
  );
}
