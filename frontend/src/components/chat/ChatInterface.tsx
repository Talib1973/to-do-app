/**
 * ChatInterface component - Main chat container with message list and input
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { sendChatMessage, getConversationHistory } from '@/lib/api/chat';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface ChatInterfaceProps {
  userId: string;
  initialConversationId?: string | null;
}

export function ChatInterface({ userId, initialConversationId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history on mount
  useEffect(() => {
    if (conversationId) {
      loadConversationHistory();
    }
  }, [conversationId]);

  const loadConversationHistory = async () => {
    if (!conversationId) return;

    try {
      setLoading(true);
      const history = await getConversationHistory(userId, conversationId);
      setMessages(history);
      setError(null);
    } catch (err) {
      console.error('Failed to load conversation history:', err);
      setError('Failed to load conversation history');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    // Optimistically add user message to UI
    const optimisticUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        userId,
        conversationId,
        message,
      });

      // Update conversation ID if it's a new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
        // Update URL with conversation ID
        window.history.replaceState(
          {},
          '',
          `/chat?conversation=${response.conversation_id}`
        );
      }

      // Replace optimistic message with server response and add assistant message
      setMessages((prev) => {
        // Remove optimistic message
        const withoutOptimistic = prev.filter(
          (m) => m.id !== optimisticUserMessage.id
        );
        // Add both user and assistant messages from server
        return [
          ...withoutOptimistic,
          {
            id: optimisticUserMessage.id,
            role: 'user',
            content: message,
            created_at: new Date().toISOString(),
          },
          response.message,
        ];
      });
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to send message. Please try again.'
      );
      // Remove optimistic message on error
      setMessages((prev) =>
        prev.filter((m) => m.id !== optimisticUserMessage.id)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700">
        <h2 className="text-xl font-semibold text-white">Task Assistant</h2>
        <p className="text-sm text-blue-100 mt-1">
          Manage your tasks with natural language
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mx-4 mt-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-sm">
                Ask me to create, view, update, or complete tasks.
              </p>
              <div className="mt-4 space-y-2 text-xs text-left bg-gray-50 rounded-lg p-4 max-w-md mx-auto">
                <p className="font-semibold text-gray-700">Try saying:</p>
                <p className="text-gray-600">• "I need to buy groceries tomorrow"</p>
                <p className="text-gray-600">• "Show me my pending tasks"</p>
                <p className="text-gray-600">• "Mark task 3 as complete"</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                role={msg.role}
                content={msg.content}
                timestamp={msg.created_at}
              />
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-3 border border-gray-200">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
}
