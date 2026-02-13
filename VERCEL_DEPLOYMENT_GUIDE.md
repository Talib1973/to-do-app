# Frontend Deployment to Vercel

## Prerequisites
- ✅ Backend deployed to Hugging Face: https://talibhussain-todo-app-deploy.hf.space
- ✅ Backend API tested and working
- ✅ Frontend working locally

## Option 1: Deploy Using Vercel Dashboard (Easiest)

### Step 1: Prepare Your Code
The frontend code is ready at: `/mnt/c/Users/DELL/Desktop/Projects/PROJECT 2/PHASE_2/frontend`

### Step 2: Go to Vercel
1. Visit: https://vercel.com/new
2. Sign in with your GitHub account (or email)

### Step 3: Import Project
You have two options:

#### A. Import from GitHub (Recommended)
1. Push your frontend code to GitHub first:
   ```bash
   cd "/mnt/c/Users/DELL/Desktop/Projects/PROJECT 2/PHASE_2/frontend"
   git init
   git add .
   git commit -m "Initial commit: Todo App Frontend"
   gh repo create todo-app-frontend --public
   git push origin main
   ```

2. On Vercel, click "Import Git Repository"
3. Select your `todo-app-frontend` repository
4. Vercel will auto-detect Next.js configuration

#### B. Upload Project Directly
1. On Vercel, click "Deploy" → "Upload"
2. Drag and drop the `frontend` folder
3. Vercel will auto-detect Next.js configuration

### Step 4: Configure Environment Variables
**CRITICAL**: Before clicking "Deploy", add environment variable:

- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://talibhussain-todo-app-deploy.hf.space`

### Step 5: Deploy
1. Click "Deploy"
2. Wait 2-3 minutes for build to complete
3. Vercel will provide your live URL (e.g., `https://todo-app-frontend.vercel.app`)

## Option 2: Deploy Using Vercel CLI

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Navigate to Frontend
```bash
cd "/mnt/c/Users/DELL/Desktop/Projects/PROJECT 2/PHASE_2/frontend"
```

### Step 3: Login to Vercel
```bash
vercel login
```

### Step 4: Deploy to Production
```bash
vercel --prod
```

The CLI will:
1. Ask you to confirm project settings (press Enter to accept defaults)
2. Build your Next.js application
3. Deploy to production
4. Provide your live URL

### Step 5: Add Environment Variable
After deployment:
```bash
vercel env add NEXT_PUBLIC_API_URL production
```
When prompted, enter: `https://talibhussain-todo-app-deploy.hf.space`

Then redeploy:
```bash
vercel --prod
```

## Testing Your Deployed Application

Once deployment is complete, test the full application:

### 1. Visit Your Vercel URL
Example: `https://todo-app-frontend.vercel.app`

### 2. Test User Registration
1. Click "Sign Up"
2. Enter name, email, and password
3. Should redirect to tasks page

### 3. Test Task Management
1. Create a new task
2. Mark task as complete
3. Edit a task
4. Delete a task

### 4. Test Login/Logout
1. Log out
2. Log back in with same credentials
3. Verify tasks are still there (data persisted)

## Troubleshooting

### If Frontend Shows "Failed to fetch" or "Network Error"

**Cause**: API URL not configured correctly

**Fix**:
1. Go to your Vercel project dashboard
2. Click "Settings" → "Environment Variables"
3. Verify `NEXT_PUBLIC_API_URL` is set to: `https://talibhussain-todo-app-deploy.hf.space`
4. Redeploy the project

### If Styling Looks Broken

**Cause**: Tailwind CSS not building correctly

**Fix**: This shouldn't happen as we have `postcss.config.js`, but if it does:
1. Check that `postcss.config.js` is in the frontend root
2. Verify `tailwind.config.ts` exists
3. Redeploy

### If Authentication Doesn't Work

**Cause**: CORS issue or API not responding

**Fix**:
1. Test backend API directly: https://talibhussain-todo-app-deploy.hf.space/docs
2. Verify CORS is configured in backend `src/main.py` to allow your Vercel domain
3. Check browser console for error messages

## Expected URLs After Deployment

- **Frontend (Vercel)**: `https://[your-project].vercel.app`
- **Backend (Hugging Face)**: `https://talibhussain-todo-app-deploy.hf.space`
- **API Docs**: `https://talibhussain-todo-app-deploy.hf.space/docs`

## Custom Domain (Optional)

To add a custom domain like `todo.yourdomain.com`:

1. Go to your Vercel project dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow Vercel's DNS configuration instructions

## Continuous Deployment

If you deployed from GitHub:
- Every push to `main` branch will automatically trigger a new deployment
- Vercel will build and deploy your changes automatically
- You can view deployment history in Vercel dashboard

## Production Checklist

Before sharing your application:
- ✅ Backend API responding correctly
- ✅ Frontend deployed and accessible
- ✅ Environment variables configured
- ✅ User signup/login working
- ✅ Task CRUD operations working
- ✅ Data persisted in Neon database
- ✅ No console errors in browser
- ✅ All features from local testing working

## Cost

- **Vercel**: Free tier includes:
  - Unlimited deployments
  - 100GB bandwidth per month
  - Automatic HTTPS
  - Perfect for this project!

- **Hugging Face**: Free tier includes:
  - Persistent storage
  - Always-on deployments
  - Perfect for this project!

- **Neon**: Free tier includes:
  - 1 project
  - 1GB storage
  - 1 branch
  - Perfect for this project!

**Total cost**: $0/month 🎉
