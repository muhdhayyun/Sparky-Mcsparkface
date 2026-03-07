import { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
} from "recharts";
import { generateDailyUsage } from "@/lib/mockData";
import { Card } from "@/components/ui/card";
import { Clock, AlertTriangle } from "lucide-react";

const UsageChart = () => {
  const data = useMemo(() => generateDailyUsage(), []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.[0]) return null;
    const point = payload[0].payload;
    return (
      <div className="bg-card border border-border rounded-lg px-3 py-2 shadow-lg">
        <p className="font-semibold text-card-foreground">{label}</p>
        <p className="text-sm text-muted-foreground">
          {point.usage} kWh
        </p>
        {point.isPeak && (
          <p className="text-xs text-peak font-medium mt-1 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" /> Peak hour
          </p>
        )}
      </div>
    );
  };

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-card-foreground">Today's Usage</h2>
          <p className="text-sm text-muted-foreground">Half-hourly electricity consumption</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-primary inline-block" /> Off-peak
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-peak inline-block" /> Peak
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="usageGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(199, 89%, 38%)" stopOpacity={0.4} />
              <stop offset="100%" stopColor="hsl(199, 89%, 38%)" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(200, 20%, 88%)" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }}
            interval={5}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }}
            unit=" kWh"
          />
          <Tooltip content={<CustomTooltip />} />
          {/* Peak bands */}
          <ReferenceArea x1="07:00" x2="09:00" fill="hsl(0, 72%, 55%)" fillOpacity={0.08} />
          <ReferenceArea x1="17:00" x2="21:00" fill="hsl(0, 72%, 55%)" fillOpacity={0.08} />
          <Area
            type="monotone"
            dataKey="usage"
            stroke="hsl(199, 89%, 38%)"
            strokeWidth={2}
            fill="url(#usageGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
        <Clock className="h-3.5 w-3.5" />
        <span>Peak hours: 7–9 AM & 5–9 PM. Shifting usage outside these windows saves you money.</span>
      </div>
    </Card>
  );
};

export default UsageChart;
