import { impactStats } from "@/lib/mockData";
import { Card } from "@/components/ui/card";
import { DollarSign, Leaf, TrendingDown, Flame, Users } from "lucide-react";

const stats = [
  {
    label: "Monthly Savings",
    value: `$${impactStats.monthlySavings}`,
    icon: DollarSign,
    color: "text-off-peak",
    bgColor: "bg-off-peak/10",
  },
  {
    label: "Carbon Reduced",
    value: `${impactStats.carbonReduced} kg`,
    icon: Leaf,
    color: "text-secondary",
    bgColor: "bg-secondary/10",
  },
  {
    label: "Peak Reduction",
    value: `${impactStats.peakReduction}%`,
    icon: TrendingDown,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    label: "Day Streak",
    value: `${impactStats.streak} 🔥`,
    icon: Flame,
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
];

const ImpactCards = () => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {stats.map((s) => (
        <Card key={s.label} className="p-4 flex flex-col items-center text-center gap-2">
          <div className={`${s.bgColor} ${s.color} p-2.5 rounded-full`}>
            <s.icon className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold text-card-foreground">{s.value}</span>
          <span className="text-xs text-muted-foreground">{s.label}</span>
        </Card>
      ))}
    </div>
  );
};

export default ImpactCards;
