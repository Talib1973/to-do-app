# Todo App Frontend

Next.js 14 frontend application with TypeScript, Tailwind CSS, and JWT authentication.

## Features

- ✅ User authentication (signup, login, logout)
- ✅ Task management (create, read, update, delete)
- ✅ Task filtering (all, pending, completed)
- ✅ Inline task editing
- ✅ Real-time UI updates
- ✅ Responsive design
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local`:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router pages
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Landing page (/)
│   │   ├── login/page.tsx        # Login page
│   │   ├── signup/page.tsx       # Signup page
│   │   ├── dashboard/page.tsx    # Dashboard (protected)
│   │   ├── error.tsx             # Error boundary
│   │   ├── not-found.tsx         # 404 page
│   │   └── globals.css           # Global styles
│   ├── components/               # React components
│   │   ├── auth/                 # Auth components
│   │   ├── tasks/                # Task components
│   │   ├── ui/                   # Base UI components
│   │   └── layout/               # Layout components
│   ├── lib/                      # Utilities
│   │   └── api/                  # API client
│   ├── types/                    # TypeScript definitions
│   └── middleware.ts             # Route middleware
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Pages

- **/** - Landing page with app description
- **/signup** - User registration
- **/login** - User authentication
- **/dashboard** - Task management (requires auth)
- **/404** - Not found page
- **/error** - Error boundary

## Components

### Authentication
- `LoginForm` - Email/password login
- `SignupForm` - User registration with validation
- `LogoutButton` - Clear session and redirect

### Task Management
- `TaskList` - Display tasks with empty state
- `TaskItem` - Task with checkbox, edit, delete
- `TaskForm` - Create new tasks
- `TaskFilter` - Filter by all/pending/completed

### UI Components
- `Input` - Text input with validation
- `Button` - Button with loading states
- `Checkbox` - Checkbox with label

### Layout
- `Header` - App header with navigation
- `Container` - Responsive container
- `Card` - Card wrapper with shadow

## API Integration

The app integrates with the FastAPI backend at `NEXT_PUBLIC_API_URL`.

### Endpoints Used

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/tasks` - List tasks (with optional ?completed filter)
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Authentication

- JWT tokens stored in localStorage
- Authorization header: `Bearer <token>`
- Auto-redirect to /login on 401 Unauthorized

## Development

### Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3
- **State**: React hooks (useState, useEffect)
- **Routing**: Next.js navigation

### Code Quality

- TypeScript strict mode
- ESLint configuration
- Tailwind CSS utilities
- Responsive design patterns

## Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-url.com
   ```

3. Deploy to Vercel:
   ```bash
   vercel deploy
   ```

## Notes

- Authentication uses localStorage (client-side)
- Route protection handled client-side in page components
- All API calls include JWT token when available
- Error handling with user-friendly messages
- Loading states on all async operations
# Force rebuild Sat Feb  7 04:42:04 PST 2026
