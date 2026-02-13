/**
 * Chat page - AI-powered task management assistant
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { Container } from '@/components/layout/Container';
import { Header } from '@/components/layout/Header';

// Force dynamic rendering for this page
export const dynamic = 'force-dynamic';

export default function ChatPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Get conversation ID from URL query parameter
  const conversationId = searchParams.get('conversation');

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      // Redirect to login if not authenticated
      router.push('/login');
      return;
    }

    try {
      setUser(JSON.parse(userData));
    } catch (err) {
      console.error('Failed to parse user data:', err);
      router.push('/login');
      return;
    } finally {
      setLoading(false);
    }
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chat...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Container>
        <div className="py-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Task Assistant</h1>
              <p className="text-gray-600 mt-2">
                Chat with AI to manage your tasks using natural language
              </p>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Back to Dashboard
            </button>
          </div>

          {/* Chat Interface */}
          <div className="h-[calc(100vh-16rem)]">
            <ChatInterface
              userId={user.id}
              initialConversationId={conversationId}
            />
          </div>

          {/* Help text */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">
              💡 Tips for chatting with the assistant:
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Create tasks:</strong> "I need to buy groceries" or "Add a task to call mom"</li>
              <li>• <strong>View tasks:</strong> "Show my tasks" or "What's pending?"</li>
              <li>• <strong>Complete tasks:</strong> "Mark task 3 done" or "I finished buying groceries"</li>
              <li>• <strong>Update tasks:</strong> "Change task 1 to 'Call mom at 6pm'"</li>
              <li>• <strong>Delete tasks:</strong> "Delete the meeting task"</li>
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
