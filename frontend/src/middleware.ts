import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Get the pathname
  const path = request.nextUrl.pathname;

  // Define public paths that don't require authentication
  const isPublicPath = path === '/' || path === '/login' || path === '/signup';

  // Define protected paths that require authentication
  const isProtectedPath = path.startsWith('/dashboard');

  // Get token from cookie (Note: in a real app, we'd check the cookie)
  // Since we're using localStorage, we can't check it server-side
  // This middleware provides basic structure but actual auth check happens client-side

  // For demo purposes, allow all requests to proceed
  // In production with proper session management, you would:
  // 1. Check for valid session cookie
  // 2. Redirect unauthorized users from protected routes
  // 3. Redirect authorized users away from auth pages

  return NextResponse.next();
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
