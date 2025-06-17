import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { SendHorizonal } from "lucide-react";

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi 👋 — ask me anything about company policies!" },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    if (!input.trim() || isSending) return;
    setIsSending(true);

    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: input }),
      });

      const data = await res.json();
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "bot", text: data.answer }]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="w-full max-w-2xl flex flex-col gap-2">
      <div className="flex-grow space-y-2 overflow-y-auto p-2 rounded-lg bg-white shadow h-[70vh]">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          className="flex-grow border rounded-xl p-3 shadow-sm"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={isSending}
        />
        <button
          onClick={send}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-4 flex items-center gap-1"
          disabled={isSending}
        >
          <SendHorizonal size={18} strokeWidth={2} /> Send
        </button>
      </div>
    </div>
  );
}
