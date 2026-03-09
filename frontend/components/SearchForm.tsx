"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchForm() {
  const router = useRouter();
  const [keywords, setKeywords] = useState("");
  const [budget, setBudget] = useState(2);
  const [groupSize, setGroupSize] = useState(2);
  const [preference, setPreference] = useState<"indoor" | "outdoor" | "either">("either");
  const [radiusKm, setRadiusKm] = useState(5);
  const [locating, setLocating] = useState(false);
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [locError, setLocError] = useState("");

  function getLocation() {
    setLocating(true);
    setLocError("");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLng(pos.coords.longitude);
        setLocating(false);
      },
      () => {
        setLocError("Could not get location. Using NYC default.");
        setLat(40.7580);
        setLng(-73.9855);
        setLocating(false);
      }
    );
  }

  function handleSubmit() {
    const resolvedLat = lat ?? 40.7580;
    const resolvedLng = lng ?? -73.9855;
    const params = new URLSearchParams({
      keywords,
      budget: budget.toString(),
      group_size: groupSize.toString(),
      preference,
      lat: resolvedLat.toString(),
      lng: resolvedLng.toString(),
      radius_km: radiusKm.toString(),
    });
    router.push(`/results?${params.toString()}`);
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-5">
      <div>
        <label className="block text-sm font-semibold text-gray-900">What are you looking for?</label>
        <input
          placeholder="e.g. authentic thai, outdoor brunch, live music"
          className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:ring-4 focus:ring-black/10 focus:border-gray-400 outline-none"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-900">Budget</label>
          <select
            className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 outline-none"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
          >
            <option value={1}>$ — Cheap</option>
            <option value={2}>$$ — Moderate</option>
            <option value={3}>$$$ — Pricey</option>
            <option value={4}>$$$$ — Splurge</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900">Group size</label>
          <input
            type="number"
            min={1}
            max={20}
            className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 outline-none"
            value={groupSize}
            onChange={(e) => setGroupSize(Number(e.target.value))}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900">Preference</label>
        <div className="mt-2 flex gap-3">
          {(["indoor", "outdoor", "either"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPreference(p)}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold border capitalize ${
                preference === p
                  ? "bg-black text-white border-black"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900">
          Radius: {radiusKm} km
        </label>
        <input
          type="range"
          min={1}
          max={20}
          value={radiusKm}
          onChange={(e) => setRadiusKm(Number(e.target.value))}
          className="mt-2 w-full"
        />
      </div>

      <div>
        <button
          onClick={getLocation}
          disabled={locating}
          className="text-sm font-semibold text-gray-600 hover:text-black underline"
        >
          {locating ? "Getting location..." : lat ? "✓ Location set" : "Use my location"}
        </button>
        {locError && <p className="text-xs text-red-500 mt-1">{locError}</p>}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!keywords.trim()}
        className="w-full bg-black text-white py-3 rounded-xl font-semibold hover:bg-gray-900 disabled:opacity-50"
      >
        Find places
      </button>
    </div>
  );
}