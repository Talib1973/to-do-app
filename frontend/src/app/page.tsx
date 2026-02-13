import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { Container } from '@/components/layout/Container';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header isAuthenticated={false} />

      <main className="flex-1 flex items-center justify-center">
        <Container>
          <div className="max-w-2xl mx-auto text-center py-16">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Welcome to Todo App
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              A simple and powerful task management application.
              Organize your tasks, boost your productivity.
            </p>

            <div className="flex gap-4 justify-center">
              <Link
                href="/signup"
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-lg transition-colors"
              >
                Get Started
              </Link>
              <Link
                href="/login"
                className="px-8 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium text-lg transition-colors"
              >
                Log In
              </Link>
            </div>
          </div>
        </Container>
      </main>
    </div>
  );
}
