import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../shared/index.css'
import ManagementApp from './ManagementApp.tsx'

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ManagementApp />
    </StrictMode>,
) 