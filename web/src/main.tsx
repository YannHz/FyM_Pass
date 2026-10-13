import { iniciarTema } from './SelectorTema'
import { PuestoAsistencia } from './PuestoAsistencia'
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Aplicacion } from "./App";
import "./index.css";

iniciarTema();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {window.location.pathname === '/puesto' ? <PuestoAsistencia /> : <Aplicacion />}
  </StrictMode>,
);
