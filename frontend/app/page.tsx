/**
 * Main page - Chat application entry point
 */
"use client";

import { useEffect, useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import { api } from "@/lib/api";

export default function Home() {
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeUser = async () => {
      try {
        // Check if user ID exists in localStorage
        let storedUserId = localStorage.getItem("disha_user_id");

        if (storedUserId) {
          // Verify user exists
          try {
            await api.getUser(storedUserId);
            setUserId(storedUserId);
          } catch {
            // User doesn't exist, create new one
            storedUserId = null;
          }
        }

        if (!storedUserId) {
          // Create new user
          const user = await api.createUser("User", { demo: true });
          localStorage.setItem("disha_user_id", user.id);
          setUserId(user.id);
        }
      } catch (err) {
        console.error("Error initializing user:", err);
        setError(
          "Failed to initialize. Please check if the backend server is running."
        );
      } finally {
        setIsLoading(false);
      }
    };

    initializeUser();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-whatsapp-green mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Disha</h2>
          <p className="text-gray-600">Your AI Health Coach</p>
          <p className="text-sm text-gray-500 mt-2">Initializing...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center max-w-md px-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">
            Connection Error
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="bg-gray-200 p-4 rounded-lg text-left">
            <p className="text-sm text-gray-700 font-semibold mb-2">
              To fix this:
            </p>
            <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
              <li>Make sure PostgreSQL is running</li>
              <li>Make sure Redis is running</li>
              <li>
                Start the backend server:{" "}
                <code className="bg-gray-300 px-1 rounded">
                  cd backend && uvicorn app.main:app --reload
                </code>
              </li>
              <li>Refresh this page</li>
            </ol>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-whatsapp-green text-white px-6 py-2 rounded-full hover:bg-whatsapp-dark transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!userId) {
    return null;
  }

  return <ChatInterface userId={userId} />;
}
