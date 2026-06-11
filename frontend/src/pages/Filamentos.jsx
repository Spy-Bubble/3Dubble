import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Filamentos() {
  const [filamentos, setFilamentos] = useState([]);
  const [busqueda, setBusqueda] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/api/filamentos')
      .then(respuesta => respuesta.json())
      .then(datos => setFilamentos(datos))
      .catch(error => console.error("Error de conexión:", error));
  }, []);

  // Lógica de filtrado en tiempo real
  const filamentosFiltrados = filamentos.filter(filamento => {
    const textoBuscado = busqueda.toLowerCase();
    return (
      filamento.material.toLowerCase().includes(textoBuscado) ||
      filamento.color.toLowerCase().includes(textoBuscado) ||
      filamento.marca.toLowerCase().includes(textoBuscado)
    );
  });

  return (
    <div className="min-h-screen bg-[#140505] text-white p-10">
      
      <Link to="/" className="text-white/50 hover:text-white mb-6 inline-block transition-colors text-sm tracking-widest uppercase">
        ← Volver al Inicio
      </Link>

      <h1 className="text-4xl font-bold text-[#DC2626] mb-10">Catálogo de Filamentos</h1>

      <div className="mb-10 max-w-md">
        <input 
          type="text" 
          placeholder="Buscar por material, color o marca..." 
          className="w-full bg-[#1C0909] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-[#DC2626]/50 transition-colors placeholder-white/30"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        
        {filamentosFiltrados.map((filamento) => (
          <div key={filamento.id} className="bg-[#1C0909] border border-white/5 rounded-xl p-4 hover:border-[#DC2626]/50 transition-colors group flex flex-col h-full">
            
            {/* Contenedor de la Imagen */}
            <div className="aspect-square w-full bg-black/40 rounded-lg mb-4 overflow-hidden flex items-center justify-center shrink-0">
              <img 
                src={filamento.url_imagen} 
                alt={`${filamento.material} ${filamento.color}`} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                onError={(e) => e.target.src = 'https://via.placeholder.com/300?text=Sin+Imagen'}
              />
            </div>
            
            {/* Contenedor de Información con Flex-Grow */}
            <div className="flex flex-col flex-grow justify-between">
              
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold mb-2">
                  {filamento.marca}
                </p>
                
                <div className="flex justify-between items-start gap-2">
                  {/* Datos Técnicos en Columna */}
                  <div className="flex flex-col leading-none">
                    <h2 className="text-xl font-bold text-white/90">{filamento.material}</h2>
                    <h3 className="text-sm font-medium text-white/50 mt-1.5">{filamento.color}</h3>
                  </div>
                  
                  {/* Precio alineado a la Derecha */}
                  <span className="text-2xl font-light text-[#DC2626] leading-none shrink-0">
                    ${filamento.precio}
                  </span>
                </div>
              </div>
              
              {/* Footer de la Tarjeta: Stock */}
              <div className="mt-5 pt-3 border-t border-white/5 flex justify-end">
                <span className="text-[11px] bg-black/40 border border-white/5 px-3 py-1 rounded-md text-white/50 font-mono tracking-wider">
                  STOCK: {filamento.stock}
                </span>
              </div>
              
            </div>
            
          </div>
        ))}

      </div>
    </div>
  );
}

export default Filamentos;