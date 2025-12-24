/**
 * Message bubble component - displays individual chat messages
 */
import { Message } from "@/lib/api";
import { format } from "date-fns";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  // Format timestamp in local timezone
  const formatTime = (timestamp: string) => {
    try {
      return format(new Date(timestamp), "HH:mm");
    } catch {
      return "";
    }
  };

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      } mb-4 message-enter`}
    >
      <div className={`max-w-[70%] ${isUser ? "order-2" : "order-1"}`}>
        <div
          className={`
            px-4 py-2 rounded-lg shadow-message
            ${
              isUser
                ? "bg-message-user text-black rounded-br-none"
                : "bg-message-ai text-black rounded-bl-none border border-gray-200"
            }
          `}
        >
          <p className="text-sm md:text-base whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>
        <div
          className={`flex items-center gap-1 mt-1 px-1 ${
            isUser ? "justify-end" : "justify-start"
          }`}
        >
          <span className="text-xs text-gray-500">
            {formatTime(message.created_at)}
          </span>
          {/* WhatsApp-style double tick for user messages */}
          {isUser && (
            <svg
              className="w-4 h-4 text-gray-500"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M12.354 4.354a.5.5 0 0 0-.708-.708L5 10.293 1.854 7.146a.5.5 0 1 0-.708.708l3.5 3.5a.5.5 0 0 0 .708 0l7-7zm-4.208 7-.896-.897.707-.707.543.543 6.646-6.647a.5.5 0 0 1 .708.708l-7 7a.5.5 0 0 1-.708 0z" />
              <path d="m5.354 7.146.896.897-.707.707-.897-.896a.5.5 0 1 1 .708-.708z" />
            </svg>
          )}
        </div>
      </div>

      {/* Avatar */}
      <div
        className={`flex-shrink-0 ${isUser ? "order-1 mr-2" : "order-2 ml-2"}`}
      >
        <div
          className={`
          w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold
          ${isUser ? "bg-blue-500" : "bg-whatsapp-green"}
        `}
        >
          {isUser ? "Y" : "D"}
        </div>
      </div>
    </div>
  );
}
