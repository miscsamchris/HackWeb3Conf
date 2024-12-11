# TeleGage - Landing Page and Dashboard

TeleGage Supercharge Your Telegram Community .

## Features

- Responsive dark-themed landing page
- User authentication (login and signup)
- Dashboard for community management
- Create and import community functionality
- Integration with Aptos blockchain

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- Radix UI for accessible components
- Aptos Labs Wallet Adapter

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   Create a `.env.local` file in the root directory and add necessary environment variables.

4. Run the development server:
   ```bash
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## User Flow

1. Landing Page: Users arrive at the home page, which showcases the product features, FAQs, and a call-to-action.
2. Authentication: Users can sign up or log in via the auth page.
3. Dashboard: After authentication, users are directed to the dashboard.
4. Community Management: From the dashboard, users can:
   - Create a new community
   - Import an existing community
   - View and manage their communities

## Project Structure

- `src/app`: Main application pages and routing
- `src/components`: Reusable React components
- `src/lib`: Utility functions and helpers
- `public`: Static assets

## Customization

You can start customizing the app by modifying the following files:

- `src/app/page.tsx`: Main landing page
- `src/app/dashboard/page.tsx`: Dashboard page
- `src/components`: Various components used throughout the app

