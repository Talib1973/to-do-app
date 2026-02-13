'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Container } from '@/components/layout/Container';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskFilter } from '@/components/tasks/TaskFilter';
import { tasksApi } from '@/lib/api/client';
import { Task, FilterType } from '@/types/components';

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<FilterType>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      setError('');
      const completed = filter === 'all' ? undefined : filter === 'completed';
      const data = await tasksApi.list(completed);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const handleCreateTask = async (title: string, description: string) => {
    const newTask = await tasksApi.create({
      title,
      description: description || undefined,
      completed: false,
    });
    setTasks((prev) => [newTask, ...prev]);
  };

  const handleToggleTask = async (taskId: string, completed: boolean) => {
    await tasksApi.patch(taskId, { completed });
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, completed } : task
      )
    );
  };

  const handleDeleteTask = async (taskId: string) => {
    await tasksApi.delete(taskId);
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const handleEditTask = async (taskId: string, title: string, description: string | null) => {
    await tasksApi.patch(taskId, { title, description: description || undefined });
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, title, description } : task
      )
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header isAuthenticated={true} />
        <main className="flex-1 flex items-center justify-center">
          <p className="text-gray-600">Loading...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header isAuthenticated={true} />

      <main className="flex-1 py-8">
        <Container>
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <button
              onClick={() => router.push('/chat')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              <span className="text-xl">💬</span>
              <span className="font-medium">Chat Assistant</span>
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <TaskForm onSubmit={handleCreateTask} />
            </div>

            <div className="lg:col-span-2 space-y-6">
              <TaskFilter activeFilter={filter} onChange={setFilter} />
              <TaskList
                tasks={tasks}
                onToggle={handleToggleTask}
                onDelete={handleDeleteTask}
                onEdit={handleEditTask}
              />
            </div>
          </div>
        </Container>
      </main>
    </div>
  );
}
