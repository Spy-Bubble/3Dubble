import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'; // Importamos el renderizador
import remarkGfm from 'remark-gfm';

function Soporte() {
  const [mensajes, setMensajes] = useState([
    { remitente: 'agente', texto: '¡Hola! Soy el sistema de soporte IA de 3Dubble. ¿En qué te puedo ayudar hoy?' }
  ]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  
  // Referencia para el Auto-Scroll
  const mensajesFinRef = useRef(null);

  // Efecto que baja la barra de scroll automáticamente cuando hay un nuevo mensaje
  useEffect(() => {
    mensajesFinRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes, cargando]);

  const enviarMensaje = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const textoUsuario = input;
    setMensajes((prev) => [...prev, { remitente: 'usuario', texto: textoUsuario }]);
    setInput('');
    setCargando(true);

    try {
      const respuesta = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          texto: textoUsuario,
          historial: mensajes
        })
      });
      
      const datos = await respuesta.json();
      setMensajes((prev) => [...prev, { remitente: 'agente', texto: datos.respuesta }]);
    } catch (error) {
      console.error("Error:", error);
      setMensajes((prev) => [...prev, { remitente: 'agente', texto: '⚠️ Error de conexión con el servidor.' }]);
    } finally {
      setCargando(false);
    }
  };

  return (
    // Fondo con gradiente sutil para darle volumen y calidez
    <div className="min-h-screen bg-gradient-to-br from-[#0A0A0A] via-[#16100e] to-[#0A0A0A] text-white p-10 flex flex-col items-center">
      
      <div className="w-full max-w-5xl flex justify-between items-center mb-8">
        <Link to="/" className="text-white/50 hover:text-[#E87A5D] transition-colors text-sm tracking-widest uppercase">
          ← Volver al Inicio
        </Link>
        <h1 className="text-2xl font-bold text-white/90">Soporte <span className="text-[#E87A5D] font-black animate-color-wheel">IA</span></h1>
      </div>

      {/* Contenedor principal del Chat con borde iluminado sutilmente */}
      <div className="w-full max-w-5xl bg-[#121212]/80 backdrop-blur-md border border-[#E87A5D]/10 rounded-2xl flex flex-col h-[85vh] shadow-[0_0_40px_rgba(0,0,0,0.5)]">
        
        {/* Historial de Mensajes */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {mensajes.map((msg, index) => (
            <div key={index} className={`flex ${msg.remitente === 'usuario' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-5 rounded-2xl text-sm leading-relaxed ${
                msg.remitente === 'usuario' 
                  ? 'bg-gradient-to-r from-[#E87A5D] to-[#D66A4D] text-black font-medium rounded-br-none shadow-lg' 
                  : 'bg-white/5 border border-white/10 text-white/90 rounded-bl-none shadow-inner'
              }`}>
                {/* El agente ahora habla en Markdown renderizado */}
                {msg.remitente === 'agente' ? (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      strong: ({node, ...props}) => <strong className="font-bold text-[#E87A5D]" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc ml-5 mt-2 space-y-1" {...props} />,
                      p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
                      // Estilos para que la tabla se vea profesional
                      table: ({node, ...props}) => (
                        <div className="overflow-x-auto my-4 rounded-lg border border-white/10">
                          <table className="min-w-full text-left text-sm border-collapse" {...props} />
                        </div>
                      ),
                      img: ({node, ...props}) => <img className="max-w-full md:max-w-md rounded-xl mt-4 border border-white/10 shadow-lg" {...props} />,
                      th: ({node, ...props}) => <th className="bg-white/5 px-4 py-3 border-b border-white/10 font-bold text-[#E87A5D]" {...props} />,
                      td: ({node, ...props}) => <td className="px-4 py-3 border-b border-white/5" {...props} />
                    }}
                  >
                    {msg.texto}
                  </ReactMarkdown>
                ) : (
                  msg.texto
                )}
              </div>
            </div>
          ))}
          
          {/* Indicador de "Escribiendo..." */}
          {cargando && (
            <div className="flex justify-start">
              <div className="bg-white/5 border border-white/10 p-4 rounded-2xl rounded-bl-none text-white/50 text-xs flex items-center gap-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-[#E87A5D]/60 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-[#E87A5D]/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                  <span className="w-2 h-2 bg-[#E87A5D]/60 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                </div>
                Consultando inventario...
              </div>
            </div>
          )}
          
          {/* Ancla invisible para el Auto-Scroll */}
          <div ref={mensajesFinRef} />
        </div>

        {/* Input de Texto */}
        <div className="p-4 border-t border-white/10 bg-[#0A0A0A]/50 rounded-b-2xl">
          <form onSubmit={enviarMensaje} className="flex gap-4">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Pregunta por un filamento, refacción o impresora..." 
              className="flex-1 bg-[#1A1A1A] border border-white/10 rounded-xl p-4 text-sm text-white focus:outline-none focus:border-[#E87A5D]/50 focus:shadow-[0_0_15px_rgba(232,122,93,0.1)] transition-all"
              disabled={cargando}
            />
            {/* Botón con efecto Glow */}
            <button 
              type="submit" 
              disabled={cargando || !input.trim()}
              className="bg-[#E87A5D] hover:bg-[#D66A4D] disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold px-8 rounded-xl transition-all duration-300 tracking-widest text-sm uppercase hover:shadow-[0_0_20px_rgba(232,122,93,0.4)]"
            >
              Enviar
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}

export default Soporte;