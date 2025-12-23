/**
 * Typing indicator component - animated dots
 */
export default function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 p-3">
      <div className="w-2 h-2 bg-gray-500 rounded-full typing-dot"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full typing-dot"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full typing-dot"></div>
    </div>
  );
}
