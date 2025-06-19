import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { SendHorizonal, ThumbsUp, ThumbsDown, Info, Star } from "lucide-react";

export default function EnhancedChat() {
  const [messages, setMessages] = useState([
    { 
      id: 1,
      role: "bot", 
      text: "Hi 👋 — I'm your enhanced company policy assistant! Ask me anything about company policies, and I'll provide detailed answers with confidence scores and sources.",
      confidence: 1.0,
      sources: [],
      context_used: false,
      timestamp: new Date().toISOString()
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [showFeedback, setShowFeedback] = useState({});
  const [feedbackScores, setFeedbackScores] = useState({});
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    if (!input.trim() || isSending) return;
    setIsSending(true);

    const userMsg = { 
      id: Date.now(),
      role: "user", 
      text: input,
      timestamp: new Date().toISOString()
    };
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
      
      const botMsg = { 
        id: Date.now() + 1,
        role: "bot", 
        text: data.answer,
        confidence: data.confidence,
        sources: data.sources,
        context_used: data.context_used,
        docsFound: data.docs_found || 0,
        responseType: data.response_type || 'unknown',
        timestamp: new Date().toISOString()
      };
      
      setMessages((m) => [...m, botMsg]);
      
      // Show feedback option for bot messages
      setShowFeedback(prev => ({ ...prev, [botMsg.id]: true }));
      
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((m) => [...m, { 
        id: Date.now() + 1,
        role: "bot", 
        text: "Sorry, I encountered an error. Please try again.",
        confidence: 0.0,
        sources: [],
        context_used: false,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsSending(false);
    }
  }

  async function submitFeedback(messageIndex, score) {
    const message = messages[messageIndex];
    if (!message || message.role !== "bot") return;

    try {
      const res = await fetch("http://localhost:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: messages[messageIndex - 1]?.text || "",
          bot_response: message.text,
          feedback_score: score,
          feedback_text: null
        }),
      });

      if (res.ok) {
        setFeedbackScores(prev => ({ ...prev, [messageIndex]: score }));
        setShowFeedback(prev => ({ ...prev, [messageIndex]: false }));
      }
    } catch (err) {
      console.error("Feedback error:", err);
    }
  }

  function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  }

  function getConfidenceText(confidence) {
    if (confidence >= 0.8) return "High";
    if (confidence >= 0.6) return "Medium";
    return "Low";
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-800">Company RAG Chatbot</h1>
        <p className="text-sm text-gray-600 mt-1">
          Ask questions about company policies and documents
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : message.isError
                  ? 'bg-red-100 text-red-800'
                  : 'bg-white text-gray-800 shadow-sm border'
              }`}
            >
              <div className="text-sm">{message.text}</div>
              
              {/* Enhanced metadata for bot messages */}
              {message.role === 'bot' && !message.isError && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-2">
                      {/* Response type indicator */}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        message.responseType === 'company_docs' 
                          ? 'bg-green-100 text-green-800' 
                          : message.responseType === 'generic'
                          ? 'bg-yellow-100 text-yellow-800'
                          : message.responseType === 'small_talk'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {message.responseType === 'company_docs' ? '📄 Company Docs' :
                         message.responseType === 'generic' ? '💭 Generic' :
                         message.responseType === 'small_talk' ? '💬 Small Talk' :
                         message.responseType}
                      </span>
                      
                      {/* Confidence score */}
                      {message.confidence !== undefined && (
                        <span className="text-xs">
                          🎯 {Math.round(message.confidence * 100)}%
                        </span>
                      )}
                      
                      {/* Documents found */}
                      {message.docsFound > 0 && (
                        <span className="text-xs">
                          📚 {message.docsFound} docs
                        </span>
                      )}
                    </div>
                    
                    <span className="text-xs">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-gray-500 mb-1">Sources:</div>
                      <div className="space-y-1">
                        {message.sources.map((source, index) => (
                          <div key={index} className="text-xs bg-gray-50 px-2 py-1 rounded">
                            📄 {source.source} ({source.chunk_type || 'N/A'})
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Feedback */}
                  {showFeedback[message.id] && (
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      <div className="text-xs text-gray-500 mb-2">Was this helpful?</div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => submitFeedback(messages.indexOf(message), 1)}
                          className="text-xs px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                        >
                          👍 Yes
                        </button>
                        <button
                          onClick={() => submitFeedback(messages.indexOf(message), 0)}
                          className="text-xs px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          👎 No
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isSending && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 rounded-lg px-4 py-3 shadow-sm border">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && send()}
            placeholder="Ask about company policies..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSending}
          />
          <button
            onClick={send}
            disabled={isSending || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
      
      <div ref={bottomRef} />
    </div>
  );
} 