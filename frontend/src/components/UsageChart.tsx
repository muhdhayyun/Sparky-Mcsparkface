import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card } from "@/components/ui/card";

interface MonthlyData {
  month: string;
  allUsersAvg: number;
  userUsage: number;
}

interface UsageChartProps {
  selectedDataset: string;
  selectedUserLabel: string;
}

const UsageChart = ({ selectedDataset, selectedUserLabel }: UsageChartProps) => {
  const [data, setData] = useState<MonthlyData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams();
    if (selectedDataset) {
      params.set("dataset", selectedDataset);
    }

    fetch(`http://localhost:3001/api/monthly-usage?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch monthly usage:', err);
        setLoading(false);
      });
  }, [selectedDataset]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload) return null;
    return (
      <div className="bg-card border border-border rounded-lg px-3 py-2 shadow-lg">
        <p className="font-semibold text-card-foreground">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {entry.value} kWh
          </p>
        ))}
      </div>
    );
  };

  return (
    <Card className="p-5">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-card-foreground">Monthly Usage 2014</h2>
        <p className="text-sm text-muted-foreground">Average monthly consumption vs. {selectedUserLabel || "your"} usage</p>
      </div>
      {loading ? (
        <div className="h-[260px] flex items-center justify-center text-muted-foreground">
          Loading...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(200, 20%, 88%)" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }}
              label={{ value: 'kWh', angle: -90, position: 'insideLeft', style: { fontSize: 10 } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: '12px' }}
              iconType="line"
            />
            <Line
              type="monotone"
              dataKey="allUsersAvg"
              name="All Users Avg"
              stroke="hsl(199, 89%, 38%)"
              strokeWidth={2}
              dot={{ r: 3 }}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="userUsage"
              name={`${selectedUserLabel || "Your"} Usage`}
              stroke="hsl(25, 95%, 53%)"
              strokeWidth={2}
              dot={{ r: 3 }}
              animationDuration={250}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
};

export default UsageChart;
