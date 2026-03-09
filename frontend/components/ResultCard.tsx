import { RecommendationItem } from "@/lib/api";

function getPriceLabel(level: number | null) {
  if (!level) return null;
  return "$".repeat(level);
}

export default function ResultCard({
  item,
  rank,
}: {
  item: RecommendationItem;
  rank: number;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl font-bold text-gray-200">#{rank}</span>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{item.name}</h2>
            <p className="text-sm text-gray-500 mt-1">{item.why}</p>
            <p className="text-xs text-gray-400 mt-1">{item.distance_km} km away</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          {item.price_level && (
            <span className="text-sm font-semibold text-gray-700">
              {getPriceLabel(item.price_level)}
            </span>
          )}
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-lg">
            {Math.round(item.score * 100)}% match
          </span>
        </div>
      </div>
    </div>
  );
}