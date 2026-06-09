import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Filamentos from './pages/Filamentos';
import Impresoras from './pages/Impresoras';
import Accesorios from './pages/Accesorios';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tienda/filamentos" element={<Filamentos />} />
        <Route path="/tienda/impresoras" element={<Impresoras />} />
        <Route path="/tienda/accesorios" element={<Accesorios />} />
      </Routes>
    </Router>
  );
}

export default App;