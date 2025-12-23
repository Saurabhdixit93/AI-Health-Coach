/**
 * Main chat interface component with infinite scroll and real-time messaging
 */
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { api, Message } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [initialLoad, setInitialLoad] = useState(true);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isNearBottom, setIsNearBottom] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const prevMessageCountRef = useRef<number>(0);

  // Check if user is near bottom of scroll
  const checkIfNearBottom = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return true;

    const threshold = 150; // pixels from bottom
    const isNear =
      container.scrollHeight - container.scrollTop - container.clientHeight <
      threshold;
    return isNear;
  }, []);

  // Scroll to bottom
  const scrollToBottom = (smooth: boolean = true) => {
    messagesEndRef.current?.scrollIntoView({
      behavior: smooth ? "smooth" : "auto",
    });
    setShowScrollButton(false);
    setIsNearBottom(true);
  };

  // Load initial messages
  const loadInitialMessages = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.getMessages(userId, undefined, 50);
      setMessages(response.messages);
      setHasMore(response.has_more);
      setNextCursor(response.next_cursor);
      setInitialLoad(false);
      // Scroll to bottom without animation on initial load
      setTimeout(() => scrollToBottom(false), 100);
    } catch (error) {
      console.error("Error loading messages:", error);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Load more messages (infinite scroll)
  const loadMoreMessages = useCallback(async () => {
    if (!hasMore || isLoadingMore || !nextCursor) return;

    try {
      setIsLoadingMore(true);
      const container = messagesContainerRef.current;
      const scrollHeightBefore = container?.scrollHeight || 0;
      const scrollTopBefore = container?.scrollTop || 0;

      const response = await api.getMessages(userId, nextCursor, 50);

      // Prepend older messages
      setMessages((prev) => [...response.messages, ...prev]);
      setHasMore(response.has_more);
      setNextCursor(response.next_cursor);

      // Maintain scroll position
      setTimeout(() => {
        if (container) {
          const scrollHeightAfter = container.scrollHeight;
          const scrollHeightDiff = scrollHeightAfter - scrollHeightBefore;
          container.scrollTop = scrollTopBefore + scrollHeightDiff;
        }
      }, 50);
    } catch (error) {
      console.error("Error loading more messages:", error);
    } finally {
      setIsLoadingMore(false);
    }
  }, [userId, hasMore, isLoadingMore, nextCursor]);

  // Handle scroll for infinite loading and scroll button
  const handleScroll = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    // Check if near bottom
    const nearBottom = checkIfNearBottom();
    setIsNearBottom(nearBottom);
    setShowScrollButton(!nearBottom);

    // Load more if scrolled near top
    if (container.scrollTop < 200 && hasMore && !isLoadingMore) {
      loadMoreMessages();
    }
  }, [hasMore, isLoadingMore, loadMoreMessages, checkIfNearBottom]);

  // Send message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const content = inputValue.trim();
    if (!content || isTyping) return;

    setInputValue("");
    setIsTyping(true);

    // Remember if we should auto-scroll
    const shouldAutoScroll = isNearBottom;

    try {
      const response = await api.sendMessage(userId, content);

      // Add both messages to state
      setMessages((prev) => [
        ...prev,
        response.user_message,
        response.ai_response,
      ]);

      // Only auto-scroll if user was near bottom
      if (shouldAutoScroll) {
        setTimeout(() => scrollToBottom(), 100);
      } else {
        setShowScrollButton(true);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message. Please try again.");
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);

    // Auto-resize
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Load initial messages on mount
  useEffect(() => {
    loadInitialMessages();
  }, [loadInitialMessages]);

  // Auto-scroll on new messages (only if near bottom)
  useEffect(() => {
    if (
      messages.length > prevMessageCountRef.current &&
      prevMessageCountRef.current > 0
    ) {
      // New messages arrived
      if (isNearBottom) {
        setTimeout(() => scrollToBottom(true), 100);
      } else {
        setShowScrollButton(true);
      }
    }
    prevMessageCountRef.current = messages.length;
  }, [messages, isNearBottom]);

  // Poll typing indicator
  useEffect(() => {
    if (isTyping) {
      const interval = setInterval(async () => {
        try {
          const status = await api.getTypingStatus(userId);
          if (!status.is_typing) {
            setIsTyping(false);
          }
        } catch (error) {
          console.error("Error checking typing status:", error);
        }
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isTyping, userId]);

  if (isLoading && initialLoad) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp-green mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-whatsapp-dark text-white px-4 py-3 shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-whatsapp-green rounded-full flex items-center justify-center font-bold">
            D
          </div>
          <div>
            <h1 className="font-semibold text-lg">Disha</h1>
            <p className="text-xs text-gray-300">Your AI Health Coach</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-2"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h100v100H0z' fill='%23e5ddd5'/%3E%3C/svg%3E\")",
        }}
      >
        {/* Load more indicator */}
        {isLoadingMore && (
          <div className="text-center py-2">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-whatsapp-green"></div>
          </div>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-message-ai rounded-lg shadow-message max-w-[70%]">
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll to bottom button */}
      {showScrollButton && (
        <button
          onClick={() => scrollToBottom(true)}
          className="
            fixed bottom-24 right-6 z-10
            bg-whatsapp-green text-white rounded-full
            w-12 h-12 shadow-lg
            flex items-center justify-center
            hover:bg-whatsapp-dark transition-all
            animate-bounce
          "
          aria-label="Scroll to bottom"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3"
            />
          </svg>
        </button>
      )}

      {/* Input */}
      <div className="bg-gray-200 px-4 py-3 border-t border-gray-300">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="
              flex-1 px-4 py-2 rounded-full border border-gray-300 
              focus:outline-none focus:ring-2 focus:ring-whatsapp-green
              resize-none overflow-hidden bg-white
            "
            rows={1}
            disabled={isTyping}
            style={{ minHeight: "40px", maxHeight: "120px" }}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="
              bg-whatsapp-green text-white rounded-full w-12 h-12
              flex items-center justify-center
              disabled:opacity-50 disabled:cursor-not-allowed
              hover:bg-whatsapp-dark transition-colors
              flex-shrink-0
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
              />
            </svg>
          </button>
        </form>
        <p className="text-xs text-gray-500 text-center mt-2">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
