import React, { useState } from 'react';
import impresoraImg from './assets/impresora.png'; 
import filamentoImg from './assets/filamento.png'; 
import accesoriosImg from './assets/accesorios.png'; 

function App() {
  // 1. NUESTRA BASE DE DATOS LOCAL PARA EL CARRUSEL
const tarjetas = [
    {
      id: 0,
      titulo: "Impresoras",
      subtitulo: "3D.",
      imagen: impresoraImg,
      colorFondo: "from-[#D97706] to-[#92400E]", // Oro Metalico
      colorLuzPrincipal: "bg-[#D97706]",
      colorLuzSecundaria: "bg-[#F59E0B]",
      // Ajuste independiente para la Impresora:
      // w-[60%] la hace más grande. right-[-5%] la empuja a la derecha cruzando el borde un poco.
      ajustesImagen: "w-[42%] max-w-[650px] -right-6 -top-[15%]" 
    },
    {
      id: 1,
      titulo: "Filamentos",
      subtitulo: "Premium.",
      imagen: filamentoImg,
      colorFondo: "from-[#B91C1C] to-[#7F1D1D]",
      colorLuzPrincipal: "bg-[#B91C1C]",
      colorLuzSecundaria: "bg-[#DC2626]",
      // Ajuste independiente para el Filamento:
      // w-[40%] lo hace más chico. top-1/2 y -translate-y-1/2 lo centran perfectamente.
      ajustesImagen: "w-[60%] max-w-[350px] -right-12 top-[45%] -translate-y-1/2" 
    },
    {
      id: 2,
      titulo: "Accesorios",
      subtitulo: "& Más.",
      imagen: accesoriosImg,
      colorFondo: "from-[#2563EB] to-[#1E3A8A]",
      colorLuzPrincipal: "bg-[#2563EB]",
      colorLuzSecundaria: "bg-[#60A5FA]",
      // Ajuste independiente para los Accesorios:
      ajustesImagen: "w-[55%] max-w-[550px] -right-20 top-[2%]" 
    }
  ];

  // 2. EL ESTADO DEL CARRUSEL (Iniciamos en la tarjeta 0)
  const [slideActual, setSlideActual] = useState(0);

  // 3. FUNCIONES PARA CAMBIAR DE TARJETA
  const siguienteSlide = () => {
    setSlideActual((prev) => (prev === tarjetas.length - 1 ? 0 : prev + 1));
  };

  const anteriorSlide = () => {
    setSlideActual((prev) => (prev === 0 ? tarjetas.length - 1 : prev - 1));
  };

  // Variable rápida para acceder a los datos de la tarjeta visible
  const tarjetaVisible = tarjetas[slideActual];

  return (
    <div className="relative min-h-screen bg-[#110A08] text-white font-sans overflow-hidden flex flex-col items-center transition-colors duration-1000">
      
      {/* LUCES DE FONDO DINÁMICAS (Cambian de color según el slide) */}
      <div className={`absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full mix-blend-screen filter blur-[150px] opacity-20 animate-pulse transition-colors duration-1000 ${tarjetaVisible.colorLuzPrincipal}`}></div>
      <div className={`absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full mix-blend-screen filter blur-[150px] opacity-10 animate-pulse transition-colors duration-1000 ${tarjetaVisible.colorLuzSecundaria}`} style={{ animationDelay: '2s' }}></div>

      {/* NAVBAR */}
      <nav className="relative z-50 w-full max-w-7xl flex justify-between items-center p-8">
        <div className="w-10"></div> 
        <h1 className="text-2xl tracking-[0.4em] font-light text-white/90">3DUBBLE</h1>
        <button className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition border border-white/10 backdrop-blur-sm">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </nav>

      {/* HEADER / HERO */}
      <header className="relative z-50 flex flex-col items-center mt-8 text-center px-4">
        <span className={`px-5 py-1.5 text-[10px] font-bold tracking-[0.2em] border rounded-full mb-8 transition-colors duration-1000 text-white/80 border-white/30`}>
          MANUFACTURA DIGITAL
        </span>
        <h2 className="text-5xl md:text-7xl font-light mb-4 tracking-tight">
          Imprimiendo tu <br />
          <span className={`font-black bg-gradient-to-r text-transparent bg-clip-text transition-colors duration-1000 ${tarjetaVisible.colorFondo}`}>
            Creatividad
          </span>
        </h2>
        <p className="text-white/50 max-w-lg text-sm leading-relaxed mt-4 font-light">
          De la idea al objeto. Transforma tus conceptos en realidad con nuestras opciones de impresión 3D profesional.
        </p>
      </header>

      {/* CARRUSEL */}
      <section className="relative z-50 w-full max-w-6xl mt-16 mb-12 flex items-center justify-center px-12">
        
        {/* BOTÓN IZQUIERDO */}
        <button 
          onClick={anteriorSlide}
          className="absolute left-2 md:left-8 p-4 bg-white/5 border border-white/10 rounded-full hover:bg-white/20 transition z-50 backdrop-blur-md">
          <span className="text-xl leading-none opacity-80">‹</span>
        </button>

        {/* CONTENEDOR DE LA TARJETA */}
        <div className="relative w-full max-w-4xl h-[450px] shadow-2xl group overflow-hidden transition-all duration-500">
          
          {/* FONDO DE COLOR DINÁMICO */}
          <div className={`absolute inset-0 bg-gradient-to-br transition-all duration-1000 ease-in-out ${tarjetaVisible.colorFondo}`}></div>

          {/* IMAGEN DEL PRODUCTO (Ahora usa la variable dinámica) */}
          <div className={`absolute z-10 pointer-events-none transition-all duration-700 ease-in-out ${tarjetaVisible.ajustesImagen}`}>
            <img
              key={tarjetaVisible.id} 
              src={tarjetaVisible.imagen}
              alt={tarjetaVisible.titulo}
              className="w-full h-auto object-contain drop-shadow-[0_20px_30px_rgba(0,0,0,0.5)] animate-[fade-in-right_0.5s_ease-out] group-hover:scale-105 transition-transform duration-700"
            />
          </div>

          {/* PANELES DE DESENFOQUE (Vidrio) */}
          <div className="absolute top-0 left-0 right-0 h-12 backdrop-blur-md z-20 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 right-0 h-24 backdrop-blur-md z-20 pointer-events-none"></div>
          <div className="absolute top-0 bottom-0 right-0 w-12 backdrop-blur-md z-20 pointer-events-none"></div>
          <div className="absolute top-0 bottom-0 left-0 w-12 backdrop-blur-md z-20 pointer-events-none"></div>

          {/* MARCO BLANCO */}
          <div className="absolute top-12 bottom-24 left-12 right-12 border-[3px] border-white/90 z-30 pointer-events-none transition-all duration-500"></div>

          {/* TEXTOS PRINCIPALES DINÁMICOS */}
          <div className="absolute top-16 left-16 z-40 pointer-events-none">
            <h3 className="text-5xl md:text-7xl font-black text-white leading-[1.05] tracking-tighter drop-shadow-md animate-[fade-in_0.5s_ease-out]">
              {tarjetaVisible.titulo} <br />
              {tarjetaVisible.subtitulo}
            </h3>
          </div>
          
          {/* BOTONES */}
          <div className="absolute bottom-6 left-16 z-40 flex gap-8 text-xs font-bold tracking-[0.15em] text-white uppercase">
            <button className="hover:text-black transition-colors flex items-center gap-2 group/btn bg-white/0 hover:bg-white px-3 py-2 -ml-3 rounded-full">
              Shop Collection <span className="text-lg leading-none transform group-hover/btn:translate-x-1 transition-transform">›</span>
            </button>
            <button className="text-white/70 hover:text-white transition flex items-center gap-2 group/btn">
              All Models <span className="text-lg leading-none transform group-hover/btn:translate-x-1 transition-transform">›</span>
            </button>
          </div>

        </div>

        {/* BOTÓN DERECHO */}
        <button 
          onClick={siguienteSlide}
          className="absolute right-2 md:right-8 p-4 bg-white/5 border border-white/10 rounded-full hover:bg-white/20 transition z-50 backdrop-blur-md">
          <span className="text-xl leading-none opacity-80">›</span>
        </button>

      </section>

    </div>
  );
}

export default App;