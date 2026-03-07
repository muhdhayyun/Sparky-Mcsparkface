import { Card } from "@/components/ui/card";
import { AlertTriangle, Clock } from "lucide-react";

const PeakAlert = () => {
  const now = new Date();
  const hour = now.getHours();
  const isPeak = (hour >= 7 && hour < 9) || (hour >= 17 && hour < 21);
  const nextPeak = hour < 7 ? "7:00 AM" : hour < 17 ? "5:00 PM" : "Tomorrow 7:00 AM";

  if (isPeak) {
    return (
      <Card className="p-4 border-peak/40 bg-peak/5 mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-peak/20 text-peak p-2 rounded-full animate-pulse-glow">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-card-foreground text-sm">⚡ Peak hours active</p>
            <p className="text-xs text-muted-foreground">
              Electricity rates are higher right now. Try to delay heavy appliance use.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 border-off-peak/40 bg-off-peak/5 mb-4">
      <div className="flex items-center gap-3">
        <div className="bg-off-peak/20 text-off-peak p-2 rounded-full">
          <Clock className="h-5 w-5" />
        </div>
        <div>
          <p className="font-semibold text-card-foreground text-sm">✅ Off-peak — Great time to use energy!</p>
          <p className="text-xs text-muted-foreground">
            Next peak starts at {nextPeak}. Run appliances now to save.
          </p>
        </div>
      </div>
    </Card>
  );
};

export default PeakAlert;
