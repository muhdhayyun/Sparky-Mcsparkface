import { impactStats } from "@/lib/mockData";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Users, Globe } from "lucide-react";

const CommunityImpact = () => {
  const rank = impactStats.communityRank;
  const total = impactStats.communityTotal;
  const percentile = Math.round(((total - rank) / total) * 100);

  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-3">
        <Globe className="h-5 w-5 text-primary" />
        <h2 className="text-lg font-bold text-card-foreground">Community Impact</h2>
      </div>
      <p className="text-sm text-muted-foreground mb-4">
        Your actions help stabilise the grid for everyone. You're in the <strong className="text-primary">top {100 - percentile}%</strong> of energy-efficient households in your area.
      </p>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground">Your ranking</span>
            <span className="font-semibold text-card-foreground">#{rank} of {total.toLocaleString()}</span>
          </div>
          <Progress value={percentile} className="h-2" />
        </div>
        <div className="grid grid-cols-2 gap-3 mt-4">
          <div className="bg-muted rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-card-foreground">1.2 MW</p>
            <p className="text-[10px] text-muted-foreground">Community peak reduced today</p>
          </div>
          <div className="bg-muted rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-card-foreground">847 kg</p>
            <p className="text-[10px] text-muted-foreground">CO₂ saved this week by your area</p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default CommunityImpact;
