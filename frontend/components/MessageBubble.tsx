/**
 * Message bubble component - displays individual chat messages
 */
import { Message } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  // Format timestamp
  const timeAgo = formatDistanceToNow(new Date(message.created_at), {
    addSuffix: true,
  });

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
          className={`text-xs text-gray-500 mt-1 px-1 ${
            isUser ? "text-right" : "text-left"
          }`}
        >
          {timeAgo}
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
