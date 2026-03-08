"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Place = {
  place_id: string;
  place_name: string;
  place_neighborhood: string | null;
  place_price_level: number | null;
  place_place_type: string;
  place_formatted_address: string | null;
};

export default function HomePage() {
  const router = useRouter();
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchPlaces(token);
  }, []);

  async function fetchPlaces(token: string) {
    try {
      const res = await fetch(`${apiUrl}/places/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        if (res.status === 401) {
          router.push("/login");
          return;
        }
        throw new Error("Failed to fetch places");
      }
      const data = await res.json();
      setPlaces(data.places);
    } catch {
      setError("Unable to load places.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  function getPriceLabel(level: number | null) {
    if (!level) return null;
    return "$".repeat(level);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">WhatToDo NYC</h1>
            <p className="mt-1 text-gray-600">Discover authentic places in New York City</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm font-semibold text-gray-600 hover:text-black"
          >
            Log out
          </button>
        </div>

        {loading && (
          <p className="text-gray-500 text-center py-12">Loading places...</p>
        )}

        {error && (
          <div className="border border-red-300 bg-red-50 rounded-xl px-4 py-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-4">
            {places.map((place) => (
              <div
                key={place.place_id}
                className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {place.place_name}
                    </h2>
                    {place.place_neighborhood && (
                      <p className="text-sm text-gray-500 mt-1">
                        {place.place_neighborhood}
                      </p>
                    )}
                    {place.place_formatted_address && (
                      <p className="text-sm text-gray-400 mt-1">
                        {place.place_formatted_address}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {place.place_price_level && (
                      <span className="text-sm font-semibold text-gray-700">
                        {getPriceLabel(place.place_price_level)}
                      </span>
                    )}
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-lg capitalize">
                      {place.place_place_type}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}