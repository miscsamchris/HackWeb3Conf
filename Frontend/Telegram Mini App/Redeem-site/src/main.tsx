import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { ThemeProvider } from './components/ThemeProvider.tsx'
import { AutoConnectProvider } from "./components/AutoConnectProvider";


import { WalletProvider } from './components/WalletProvider';


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AutoConnectProvider>
    <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
    <WalletProvider>
      <App />
    </WalletProvider>
    </ThemeProvider>
    </AutoConnectProvider>
  </React.StrictMode>,
)
