# Courtsight Frontend - React Application

Modern React frontend for the Courtsight basketball analysis platform.

## Tech Stack

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Modern CSS** - Dark theme, responsive design

## Getting Started

### Prerequisites

- Node.js 18+ (or 20+ recommended)
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Runs on `http://localhost:3000`

### Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:5001
```

For production, set this to your deployed backend URL:
```env
VITE_API_URL=https://your-backend.railway.app
```

### Build for Production

```bash
npm run build
```

Output will be in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Deployment

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for full deployment instructions.

### Quick Deploy to Vercel

1. Push code to GitHub
2. Go to https://vercel.com
3. Import repository
4. Set root directory to `frontend`
5. Add environment variable: `VITE_API_URL`
6. Deploy!

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main app component
│   ├── App.css          # App styles
│   ├── index.css        # Global styles
│   └── main.jsx         # Entry point
├── public/              # Static assets
├── vite.config.js       # Vite configuration
├── vercel.json          # Vercel deployment config
└── netlify.toml         # Netlify deployment config
```

## Features

- ✅ Modern, dark-themed UI
- ✅ Real-time analysis status updates
- ✅ YouTube video URL input
- ✅ Video playback after analysis
- ✅ Responsive design
- ✅ Loading states and error handling

## API Integration

The frontend communicates with the Flask backend API:

- `POST /api/analyze` - Start video analysis
- `GET /api/analysis_status/:job_id` - Check analysis status
- `GET /video/:filename` - Stream analyzed videos

See the backend documentation for full API details.

## Development Tips

- The app automatically polls for analysis status every 2 seconds
- Video URLs are validated and displayed after completion
- Error states are handled gracefully with user feedback

## License

Same as parent project.
