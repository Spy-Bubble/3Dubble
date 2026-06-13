import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Accesorios() {
  const [accesorios, setAccesorios] = useState([]);
  const [busqueda, setBusqueda] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/api/accesorios')
      .then(respuesta => respuesta.json())
      .then(datos => setAccesorios(datos))
      .catch(error => console.error("Error de conexión:", error));
  }, []);

  // Lógica de filtrado
  const accesoriosFiltrados = accesorios.filter(accesorio => {
    const textoBuscado = busqueda.toLowerCase();
    return (
      accesorio.nombre.toLowerCase().includes(textoBuscado) ||
      accesorio.compatibilidad.toLowerCase().includes(textoBuscado)
    );
  });

  return (
    <div className="min-h-screen bg-[#090D16] text-white p-10">
      
      <Link to="/" className="text-white/50 hover:text-white mb-6 inline-block transition-colors text-sm tracking-widest uppercase">
        ← Volver al Inicio
      </Link>

      <h1 className="text-4xl font-bold text-[#60A5FA] mb-10">Componentes y Refacciones</h1>

      {/*Barra de Búsqueda */}
      <div className="mb-10 max-w-md">
        <input 
          type="text" 
          placeholder="Buscar por nombre o compatibilidad..." 
          className="w-full bg-[#111827] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-[#60A5FA]/50 transition-colors placeholder-white/30"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        
        {accesoriosFiltrados.map((accesorio) => (
          <div key={accesorio.id} className="bg-[#111827] border border-white/5 rounded-xl p-4 hover:border-[#60A5FA]/40 transition-colors group flex flex-col h-full">
            
            <div className="aspect-square w-full bg-black/40 rounded-lg mb-4 overflow-hidden flex items-center justify-center shrink-0">
              <img 
                src={accesorio.url_imagen} 
                alt={accesorio.nombre} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                onError={(e) => e.target.src = 'https://via.placeholder.com/300?text=Sin+Imagen'}
              />
            </div>
            
            <div className="flex flex-col flex-grow justify-between">
              <div>
                <p className="text-[10px] text-[#60A5FA]/60 uppercase tracking-widest font-bold mb-2">
                  Compatibilidad
                </p>
                
                <div className="flex justify-between items-start gap-2">
                  <div className="flex flex-col leading-tight">
                    <h2 className="text-lg font-bold text-white/90 line-clamp-2">{accesorio.nombre}</h2>
                    <h3 className="text-xs font-medium text-white/40 mt-1">{accesorio.compatibilidad}</h3>
                  </div>
                  
                  <span className="text-2xl font-light text-[#60A5FA] leading-none shrink-0">
                    ${accesorio.precio}
                  </span>
                </div>
              </div>
            </div>
            
          </div>
        ))}

      </div>
    </div>
  );
}

export default Accesorios;