# LMS-x-DR — Learning Management × Demand Radar
# OS: ~/Desktop/Claude OS/CLAUDE.md | Dashboard: ~/Desktop/CLAUDE.md
# Load both at session start before any project work.

---

## Project Overview
AI-powered platform combining business opportunity analysis with structured learning paths and market demand tracking.

## Current State
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS v4
- **Deployment**: Live on Vercel at https://lms-x-dr.vercel.app
- **Features Implemented**:
  - 12 AI-analyzed business opportunities with scoring
  - Interactive learning paths with progress tracking
  - Responsive dark theme UI
  - Module completion tracking
  - Difficulty levels (Beginner/Intermediate/Advanced)

## Tech Stack
- **Frontend**: Next.js 15 (App Router) + TypeScript
- **Styling**: Tailwind CSS v4 + Custom CSS variables
- **Data**: Static JSON (no database yet)
- **Hosting**: Vercel (auto-deploy on push)
- **Version Control**: GitHub (tanejaashish5-collab/LMS-x-DR)

## Project Structure
```
app/
├── page.tsx                 # Main opportunity dashboard
├── layout.tsx              # App layout with metadata
├── globals.css             # Tailwind + custom styles
├── components/
│   └── LearningPath.tsx   # Learning modules component
└── data/
    └── opportunities.ts    # Static opportunity data
```

## Next Phase Priorities
1. **Demand Radar Visualization**
   - Real-time market demand indicators
   - Trend analysis charts
   - Opportunity heat maps

2. **AI Agent Integration**
   - Use 9 configured agents for analysis
   - Personalized opportunity recommendations
   - Dynamic learning path generation

3. **User Features**
   - Progress persistence (localStorage → Supabase)
   - User profiles and authentication
   - Certificate generation on completion

4. **Content Expansion**
   - Complete learning paths for all 12 opportunities
   - Add video resources and external links
   - Community discussion features

## Technical Resources (Shared from Claude OS)
Now using centralized resources from `~/Desktop/Claude OS/`:
- **Technical Agents**: `~/Desktop/Claude OS/agents/technical/`
  - architect, code-reviewer, security-reviewer, tdd-guide
  - build-error-resolver, research-agent, fullstack-builder
  - automation-architect, planner
- **Skills**: `~/Desktop/Claude OS/skills/`
  - multi-agent, memory-management, spec-driven-dev
  - design-review, continuous-learning, plan, tdd
  - code-review, security-scan
- **Rules**: `~/Desktop/Claude OS/rules/`
  - security, typescript, python, common standards

## Development Workflow
1. Plan features using `/plan` or Planner agent
2. Build with clean, readable code (functions < 50 lines)
3. Review with `/code-review`
4. Deploy via git push (auto-deploys to Vercel)

## Key URLs
- **Live Site**: https://lms-x-dr.vercel.app
- **GitHub**: https://github.com/tanejaashish5-collab/LMS-x-DR
- **Local Dev**: http://localhost:3000

## Commands
```bash
npm install     # Install dependencies
npm run dev     # Start dev server
npm run build   # Build for production
git push        # Auto-deploys to Vercel
```

## Notes
- No database integration yet (using static data)
- No user authentication (public access only)
- Learning paths only available for 2 opportunities (home-services, ar-collections)
- CSS variables properly configured for dark theme
- Viewport meta tag added for mobile responsiveness

---

*Last Updated: 2026-03-17*