'use client';

import { useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { Container } from '@/components/layout/Container';
import { Card } from '@/components/layout/Card';
import { Button } from '@/components/ui/Button';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console (in production, send to error tracking service)
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex items-center justify-center py-12">
        <Container>
          <div className="max-w-md mx-auto">
            <Card>
              <div className="text-center">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  Something went wrong!
                </h2>
                <p className="text-gray-600 mb-6">
                  We're sorry, but something unexpected happened.
                  Please try again.
                </p>
                <Button onClick={reset} variant="primary">
                  Try again
                </Button>
              </div>
            </Card>
          </div>
        </Container>
      </main>
    </div>
  );
}
