import Chat from "./components/Chat";
import './index.css';

function App() {
  return (
    <div className="bg-gray-50 min-h-screen flex flex-col items-center p-4">
      <h1 className="text-3xl font-bold mb-4">📚 Company Knowledge Assistant</h1>
      <Chat />
    </div>
  );
}

export default App;
