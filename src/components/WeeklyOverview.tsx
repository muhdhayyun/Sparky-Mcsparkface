import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { weeklyUsage } from "@/lib/mockData";
import { Card } from "@/components/ui/card";

const WeeklyOverview = () => {
  return (
    <Card className="p-5">
      <h2 className="text-lg font-bold text-card-foreground mb-1">Weekly Overview</h2>
      <p className="text-sm text-muted-foreground mb-4">Daily usage vs. your 16 kWh target</p>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={weeklyUsage} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
          <XAxis dataKey="day" tick={{ fontSize: 12, fill: "hsl(210, 15%, 45%)" }} />
          <YAxis tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }} unit=" kWh" />
          <Tooltip
            contentStyle={{
              background: "hsl(0, 0%, 100%)",
              border: "1px solid hsl(200, 20%, 88%)",
              borderRadius: "8px",
              fontSize: 12,
            }}
          />
          <ReferenceLine y={16} stroke="hsl(168, 60%, 42%)" strokeDasharray="4 4" label={{ value: "Target", position: "right", fontSize: 10, fill: "hsl(168, 60%, 42%)" }} />
          <Bar dataKey="usage" radius={[6, 6, 0, 0]} fill="hsl(199, 89%, 38%)" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default WeeklyOverview;
