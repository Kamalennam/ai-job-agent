import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthBootstrap } from './app/AuthBootstrap'
import { ThemeProvider } from './app/ThemeProvider'
import App from './App'
import './styles/index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AuthBootstrap>
          <App />
        </AuthBootstrap>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
