import { iniciarSonido } from './sonidos'
import { iniciarTema } from './SelectorTema'
import { PuestoAsistencia } from './PuestoAsistencia'
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Aplicacion } from "./App";
import "./index.css";

iniciarTema();
iniciarSonido();

if (import.meta.env.PROD && 'serviceWorker' in navigator && window.isSecureContext) {
  window.addEventListener('load', () => {
    void navigator.serviceWorker.register('/service-worker.js', { updateViaCache: 'none' }).catch(() => {})
  })
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {window.location.pathname === '/puesto' ? <PuestoAsistencia /> : <Aplicacion />}
  </StrictMode>,
);
