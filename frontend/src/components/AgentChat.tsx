import { useState } from "react";
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

      const agentText = res.data.raw || "Agent couldn't answer...";
      setMessages((prev) => [...prev, { sender: "agent", text: agentText }]);

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
    <div className="max-w-2xl mx-auto p-4">
      <div className="h-96 overflow-y-auto bg-gray-100 rounded-lg p-4 space-y-4 shadow">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>
            <strong>{msg.sender === "user" ? "You" : "Agent"}:</strong> {msg.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Need some help?..."
        />
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Send"}
        </button>
      </form>
    </div>
  );
}
