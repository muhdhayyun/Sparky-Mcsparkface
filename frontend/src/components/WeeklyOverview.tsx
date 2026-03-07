import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import { Card } from "@/components/ui/card";

interface WeeklyData {
  day: string;
  avgUsage: number;
  target: number;
}

const WeeklyOverview = () => {
  const [data, setData] = useState<WeeklyData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:3001/api/weekly-overview')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch weekly overview:', err);
        setLoading(false);
      });
  }, []);

  return (
    <Card className="p-5">
      <h2 className="text-lg font-bold text-card-foreground mb-1">Weekly Overview</h2>
      <p className="text-sm text-muted-foreground mb-4">Daily usage vs. your 16 kWh target</p>
      {loading ? (
        <div className="h-[200px] flex items-center justify-center text-muted-foreground">
          Loading...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
            <XAxis dataKey="day" tick={{ fontSize: 12, fill: "hsl(210, 15%, 45%)" }} />
            <YAxis 
              tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }} 
              label={{ value: 'kWh', angle: -90, position: 'insideLeft', style: { fontSize: 10 } }}
              domain={[0, 24]}
            />
            <Tooltip
              contentStyle={{
                background: "hsl(0, 0%, 100%)",
                border: "1px solid hsl(200, 20%, 88%)",
                borderRadius: "8px",
                fontSize: 12,
              }}
            />
            <ReferenceLine 
              y={16} 
              stroke="hsl(168, 60%, 42%)" 
              strokeDasharray="4 4" 
              label={{ value: "Target", position: "right", fontSize: 10, fill: "hsl(168, 60%, 42%)" }} 
            />
            <Bar dataKey="avgUsage" radius={[6, 6, 0, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.avgUsage > 16 ? "hsl(0, 72%, 55%)" : "hsl(199, 89%, 38%)"} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
};

export default WeeklyOverview;
