"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { fetchRecommendations, RecommendationItem } from "@/lib/api";
import ResultCard from "@/components/ResultCard";

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const [results, setResults] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchRecommendations({
          keywords: searchParams.get("keywords") || "",
          budget: Number(searchParams.get("budget") || 2),
          group_size: Number(searchParams.get("group_size") || 2),
          preference: (searchParams.get("preference") as "indoor" | "outdoor" | "either") || "either",
          lat: Number(searchParams.get("lat") || 40.758),
          lng: Number(searchParams.get("lng") || -73.9855),
          radius_km: Number(searchParams.get("radius_km") || 5),
        });
        setResults(data);
      } catch {
        setError("Could not load recommendations.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Results</h1>
            <p className="mt-1 text-gray-600">
              Showing recommendations for "{searchParams.get("keywords")}"
            </p>
          </div>
          <a href="/" className="text-sm font-semibold text-gray-600 hover:text-black">
            ← Back
          </a>
        </div>

        {loading && (
          <p className="text-gray-500 text-center py-12">Finding the best places for you...</p>
        )}

        {error && (
          <div className="border border-red-300 bg-red-50 rounded-xl px-4 py-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {!loading && !error && results.length === 0 && (
          <p className="text-gray-500 text-center py-12">
            No results found. Try a different search.
          </p>
        )}

        {!loading && !error && (
          <div className="space-y-4">
            {results.map((item, index) => (
              <ResultCard key={item.place_id} item={item} rank={index + 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}