import { useState } from "react";
import EnhancedChat from "./components/EnhancedChat";
import AdminDashboard from "./components/AdminDashboard";
import { MessageSquare, Settings } from "lucide-react";
import './index.css';

export default function App() {
  const [activeView, setActiveView] = useState("chat");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Enhanced Company RAG Chatbot
              </h1>
            </div>
            
            {/* Navigation */}
            <nav className="flex space-x-4">
              <button
                onClick={() => setActiveView("chat")}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === "chat"
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                <MessageSquare size={16} />
                Chat
              </button>
              <button
                onClick={() => setActiveView("admin")}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === "admin"
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                <Settings size={16} />
                Admin
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {activeView === "chat" ? (
          <div className="flex justify-center">
            <EnhancedChat />
          </div>
        ) : (
          <AdminDashboard />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-600">
            <p>Enhanced RAG Chatbot v2.0 • Self-training enabled • Powered by LangChain & OpenAI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
