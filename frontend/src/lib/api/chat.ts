/**
 * Chat API client methods
 */

const API_BASE_URL = 'http://localhost:8000';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

interface ChatResponse {
  conversation_id: string;
  message: Message;
  tool_calls: ToolCall[];
}

interface SendMessageParams {
  userId: string;
  conversationId: string | null;
  message: string;
}

interface ConversationHistory {
  messages: Message[];
}

export async function sendChatMessage({
  userId,
  conversationId,
  message,
}: SendMessageParams): Promise<ChatResponse> {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function getConversationHistory(
  userId: string,
  conversationId: string
): Promise<Message[]> {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/conversations/${conversationId}/messages`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}
