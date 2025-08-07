import { useState } from "react";
import axios from "axios";

interface AgentResponse {
  action?: string;
  timer?: number;
  task_name?: string;
  error?: string;
  raw?: string;
}

export function AgentChat() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AgentResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);

    try {
      const res = await axios.post("http://localhost:8000/agent/", { prompt });
      setResponse(res.data);
      
      // Si la acción es start_pomodoro, aquí podrías llamar directamente
      // a tu servicio createPomodoro o CompletedPomodoroNotif según tu lógica.
      if (res.data.action === "start_pomodoro") {
        console.log("Acción detectada:", res.data);
        // TODO: ejecutar createPomodoro(...) u otra función
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-4 max-w-xl mx-auto">
      <form onSubmit={handleSubmit} className="w-full flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Escribe algo (ej: 'Empieza un pomodoro de 25 min de mates')"
          className="flex-1 border border-gray-400 rounded-lg px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg"
        >
          {loading ? "..." : "Enviar"}
        </button>
      </form>

      {response && (
        <div className="mt-4 w-full p-3 bg-gray-100 rounded-lg text-sm">
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
