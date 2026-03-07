import { useState } from "react";
import { recommendations, type Recommendation } from "@/lib/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  WashingMachine,
  Thermometer,
  UtensilsCrossed,
  Plug,
  Snowflake,
  Check,
  ChevronRight,
} from "lucide-react";

const iconMap: Record<string, React.ElementType> = {
  "washing-machine": WashingMachine,
  thermometer: Thermometer,
  utensils: UtensilsCrossed,
  plug: Plug,
  snowflake: Snowflake,
};

const impactColor: Record<string, string> = {
  high: "bg-peak/10 text-peak border-peak/20",
  medium: "bg-accent/10 text-accent border-accent/20",
  low: "bg-muted text-muted-foreground border-border",
};

const Recommendations = () => {
  const [completed, setCompleted] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-card-foreground">Smart Recommendations</h2>
          <p className="text-sm text-muted-foreground">
            {completed.size}/{recommendations.length} actions taken
          </p>
        </div>
        {/* progress ring */}
        <div className="relative h-10 w-10">
          <svg viewBox="0 0 36 36" className="h-10 w-10 -rotate-90">
            <circle
              cx="18" cy="18" r="15"
              fill="none"
              stroke="hsl(200, 25%, 93%)"
              strokeWidth="3"
            />
            <circle
              cx="18" cy="18" r="15"
              fill="none"
              stroke="hsl(168, 60%, 42%)"
              strokeWidth="3"
              strokeDasharray={`${(completed.size / recommendations.length) * 94.25} 94.25`}
              strokeLinecap="round"
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-card-foreground">
            {Math.round((completed.size / recommendations.length) * 100)}%
          </span>
        </div>
      </div>
      <div className="space-y-3">
        {recommendations.map((rec) => {
          const Icon = iconMap[rec.icon] || Plug;
          const done = completed.has(rec.id);
          return (
            <div
              key={rec.id}
              className={`flex items-start gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                done
                  ? "bg-off-peak/5 border-off-peak/30"
                  : "bg-card border-border hover:border-primary/30"
              }`}
              onClick={() => toggle(rec.id)}
            >
              <div className={`shrink-0 p-2 rounded-lg ${done ? "bg-off-peak/20 text-off-peak" : "bg-primary/10 text-primary"}`}>
                {done ? <Check className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className={`font-semibold text-sm ${done ? "line-through text-muted-foreground" : "text-card-foreground"}`}>
                    {rec.title}
                  </span>
                  <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${impactColor[rec.impact]}`}>
                    {rec.impact}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{rec.description}</p>
                <span className="text-xs font-semibold text-off-peak mt-1 inline-block">
                  Save {rec.savings}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default Recommendations;
