import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Impresoras() {
  const [impresoras, setImpresoras] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/impresoras')
      .then(respuesta => respuesta.json())
      .then(datos => setImpresoras(datos))
      .catch(error => console.error("Error de conexión:", error));
  }, []);

  return (
    <div className="min-h-screen bg-[#140D05] text-white p-10">
      
      <Link to="/" className="text-white/50 hover:text-white mb-6 inline-block transition-colors text-sm tracking-widest uppercase">
        ← Volver al Inicio
      </Link>

      <h1 className="text-4xl font-bold text-[#D97706] mb-10">Equipos de Impresión</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        
        {impresoras.map((impresora) => (
          <div key={impresora.id} className="bg-[#1C130A] border border-white/5 rounded-xl p-4 hover:border-white/20 transition-colors group flex flex-col h-full">
            
            <div className="aspect-square w-full bg-black/40 rounded-lg mb-4 overflow-hidden flex items-center justify-center shrink-0">
              <img 
                src={impresora.url_imagen} 
                alt={impresora.modelo} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                onError={(e) => e.target.src = 'https://via.placeholder.com/300?text=Sin+Imagen'}
              />
            </div>
            
            <div className="flex flex-col flex-grow justify-between">
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold mb-2">
                  {impresora.marca}
                </p>
                
                <div className="flex justify-between items-start gap-2">
                  <div className="flex flex-col leading-none">
                    <h2 className="text-xl font-bold text-white/90">{impresora.modelo}</h2>
                    {/* Especificación técnica propia de hardware */}
                    <h3 className="text-xs font-mono text-white/40 mt-2 bg-white/5 px-1.5 py-0.5 rounded w-fit">
                      {impresora.volumen_impresion}
                    </h3>
                  </div>
                  
                  <span className="text-2xl font-light text-[#D97706] leading-none shrink-0">
                    ${impresora.precio}
                  </span>
                </div>
              </div>
              
              <div className="mt-5 pt-3 border-t border-white/5 flex justify-end">
                <span className="text-[11px] bg-black/40 border border-white/5 px-3 py-1 rounded-md text-white/50 font-mono tracking-wider">
                  STOCK: {impresora.stock}
                </span>
              </div>
            </div>
            
          </div>
        ))}

      </div>
    </div>
  );
}

export default Impresoras;