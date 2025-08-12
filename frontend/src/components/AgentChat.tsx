import { useState, useRef } from "react";
import { supabase } from "../services/supabase";
import axiosInstance from "../services/api/axiosInstance";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

interface Message {
  sender: "user" | "agent";
  text: string;
}

export function AgentChat() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { data } = await supabase.auth.getSession();
    if (!prompt.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: prompt }]);
    setLoading(true);

    try {
      const res = await axiosInstance.post(
        `${BACKEND_URL}agent/`,
        { prompt: prompt, token: data.session?.access_token },
        {
          headers: {
            Authorization: `Bearer ${data.session?.access_token}`,
            "Content-Type": "application/json",
          }
        }
      );

      const agentResponse = res.data;
      setMessages(prev => [...prev, { 
        sender: "agent", 
        text: typeof agentResponse === "string" ? agentResponse : agentResponse.output || "No response from agent"
      }]);


      if (res.data.action === "start_pomodoro") {
        console.log("Agent wants to start pomodoro:", res.data);
      }

    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { sender: "agent", text: "There was an error while trying to contact agent" }]);
    } finally {
      setPrompt("");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="h-96 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-4 shadow-inner border border-gray-200">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 h-full flex items-center justify-center">
            Start a conversation with your AI agent...
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-xs md:max-w-md rounded-lg px-4 py-2 ${
                msg.sender === "user" 
                  ? "bg-blue-500 text-white" 
                  : "bg-gray-200 text-gray-800"
              }`}>
                <strong>{msg.sender === "user" ? "You" : "Agent"}:</strong> {msg.text}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask your agent..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button 
          type="submit" 
          disabled={loading || !prompt.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300 transition-colors"
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : "Send"}
        </button>
      </form>
    </div>
  );
}