const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type RecommendationRequest = {
  keywords: string;
  budget: number;
  group_size: number;
  preference: "indoor" | "outdoor" | "either";
  lat: number;
  lng: number;
  radius_km: number;
};

export type RecommendationItem = {
  place_id: string;
  name: string;
  price_level: number | null;
  lat: number;
  lng: number;
  distance_km: number;
  score: number;
  why: string;
};

export async function fetchRecommendations(
  req: RecommendationRequest
): Promise<RecommendationItem[]> {
  const res = await fetch(`${API_URL}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error("Failed to fetch recommendations");
  const data = await res.json();
  return data.results;
}