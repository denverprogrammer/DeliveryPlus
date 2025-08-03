import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../shared/index.css'
import DeliveryApp from './DeliveryApp.tsx'

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <DeliveryApp />
    </StrictMode>,
) 