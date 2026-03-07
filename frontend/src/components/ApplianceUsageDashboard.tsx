import { Card } from "@/components/ui/card";
import { ResponsiveContainer, BarChart, XAxis, YAxis, Tooltip, ReferenceLine, Bar } from "recharts";
import { applianceUsage } from "@/lib/mockData";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useMemo } from "react";

const ApplianceUsageDashboard = () => {
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    // Filter data based on selected date range
    const filteredData = useMemo(() => {
        let data = applianceUsage;

        if (startDate) {
            data = data.filter(item => item.date >= startDate);
        }

        if (endDate) {
            data = data.filter(item => item.date <= endDate);
        }

        return data;
    }, [startDate, endDate]);

    return (
        <Card className="p-5">
            <h2 className="text-lg font-bold text-card-foreground">Appliance Usage Dashboard</h2>
            <p className="text-sm text-muted-foreground mb-4">
                How much your appliances have used over the past couple of days
            </p>

            {/* Date Filter Section */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="space-y-1">
                    <Label htmlFor="start-date" className="text-xs">From Date</Label>
                    <Input
                        id="start-date"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="text-sm"
                    />
                </div>
                <div className="space-y-1">
                    <Label htmlFor="end-date" className="text-xs">To Date</Label>
                    <Input
                        id="end-date"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="text-sm"
                    />
                </div>
            </div>

            <ResponsiveContainer width="100%" height={200}>
                <BarChart data={filteredData} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
                    <XAxis dataKey="applianceName" tick={{ fontSize: 12, fill: "hsl(210, 15%, 45%)" }} />
                              <YAxis tick={{ fontSize: 10, fill: "hsl(210, 15%, 45%)" }} unit=" hrs" />
                              <Tooltip
                                contentStyle={{
                                  background: "hsl(0, 0%, 100%)",
                                  border: "1px solid hsl(200, 20%, 88%)",
                                  borderRadius: "8px",
                                  fontSize: 12,
                                }}
                              />
                              <ReferenceLine y={16} stroke="hsl(168, 60%, 42%)" strokeDasharray="4 4" label={{ value: "Target", position: "right", fontSize: 10, fill: "hsl(168, 60%, 42%)" }} />
                              <Bar dataKey="hours" radius={[6, 6, 0, 0]} fill="hsl(199, 89%, 38%)" />
                </BarChart>
            </ResponsiveContainer>
        </Card>
    )
}

export default ApplianceUsageDashboard;