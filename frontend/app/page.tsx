"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SearchForm from "@/components/SearchForm";

export default function HomePage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("whattodo_token");
    if (!token) {
      router.push("/login");
      return;
    }
    setReady(true);
  }, []);

  function handleLogout() {
    localStorage.removeItem("whattodo_token");
    router.push("/login");
  }

  if (!ready) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">WhatToDo NYC</h1>
            <p className="mt-1 text-gray-600">
              Discover authentic places in New York City
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm font-semibold text-gray-600 hover:text-black"
          >
            Log out
          </button>
        </div>
        <SearchForm />
      </div>
    </div>
  );
}