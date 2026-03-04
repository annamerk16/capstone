"use client";

import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  function handleLogout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
      <div className="w-full max-w-md text-center">
        <h1 className="text-3xl font-bold text-gray-900">WhatToDo NYC</h1>
        <p className="mt-2 text-gray-700">You're logged in! Home page coming soon.</p>
        <button
          onClick={handleLogout}
          className="mt-6 px-6 py-3 bg-black text-white rounded-xl font-semibold hover:bg-gray-900"
        >
          Log out
        </button>
      </div>
    </div>
  );
}
