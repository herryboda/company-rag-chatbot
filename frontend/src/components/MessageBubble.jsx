export default function MessageBubble({ role, text }) {
  const isBot = role === "bot";
  return (
    <div
      className={`flex ${isBot ? "justify-start" : "justify-end"} animate-fade-in`}
    >
      <div
        className={`max-w-[75%] px-4 py-2 rounded-2xl shadow ${
          isBot ? "bg-gray-200 text-gray-900" : "bg-blue-600 text-white"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
