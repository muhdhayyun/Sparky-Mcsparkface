import { Card } from "@/components/ui/card";
import { ResponsiveContainer, BarChart, XAxis, YAxis, Tooltip, ReferenceLine, Bar } from "recharts";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useMemo, useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ApplianceData {
    id: number;
    user_id?: string;
    date: string;
    hours: number;
    appliance_name: string;
    created_at?: string;
}

interface ApplianceUsageDashboardProps {
    selectedDataset: string;
}

const ApplianceUsageDashboard = ({ selectedDataset }: ApplianceUsageDashboardProps) => {
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [applianceData, setApplianceData] = useState<ApplianceData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchApplianceData = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (selectedDataset) {
                params.set("user_id", selectedDataset);
            }

            const response = await fetch(`http://localhost:3001/api/appliances?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch appliance data');
            }
            
            const data = await response.json();
            setApplianceData(data);
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to load appliance data';
            setError(errorMsg);
            console.error('Error fetching appliance data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchApplianceData();
        
        const handleApplianceAdded = () => {
            fetchApplianceData();
        };
        
        window.addEventListener('appliance-added', handleApplianceAdded);
        
        return () => {
            window.removeEventListener('appliance-added', handleApplianceAdded);
        };
    }, [selectedDataset]);

    const filteredData = useMemo(() => {
        let data = applianceData.map(item => ({
            date: item.date,
            hours: Number(item.hours),
            applianceName: item.appliance_name
        }));

        if (startDate) {
            data = data.filter(item => item.date >= startDate);
        }

        if (endDate) {
            data = data.filter(item => item.date <= endDate);
        }

        return data;
    }, [applianceData, startDate, endDate]);

    if (loading) {
        return (
            <Card className="p-5">
                <Skeleton className="h-6 w-48 mb-2" />
                <Skeleton className="h-4 w-64 mb-4" />
                <div className="grid grid-cols-2 gap-3 mb-4">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                </div>
                <Skeleton className="h-[200px] w-full" />
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="p-5">
                <h2 className="text-lg font-bold text-card-foreground">Appliance Usage Dashboard</h2>
                <p className="text-sm text-muted-foreground mb-4">
                    How much your appliances have used
                </p>
                <div className="flex flex-col items-center justify-center py-8 text-center">
                    <AlertCircle className="h-12 w-12 text-destructive mb-3" />
                    <p className="text-sm text-muted-foreground mb-4">{error}</p>
                    <Button onClick={fetchApplianceData} size="sm" variant="outline">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Retry
                    </Button>
                </div>
            </Card>
        );
    }

    if (filteredData.length === 0) {
        return (
            <Card className="p-5">
                <h2 className="text-lg font-bold text-card-foreground">Appliance Usage Dashboard</h2>
                <p className="text-sm text-muted-foreground mb-4">
                    How much your appliances have used
                </p>
                
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

                <div className="flex flex-col items-center justify-center py-8 text-center border-2 border-dashed border-border rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">
                        {applianceData.length === 0 
                            ? "No appliances tracked yet"
                            : "No appliances found for selected date range"
                        }
                    </p>
                    <p className="text-xs text-muted-foreground">
                        {applianceData.length === 0
                            ? "Add your first appliance for this selected dataset to see usage data"
                            : "Try adjusting your date filters"
                        }
                    </p>
                </div>
            </Card>
        );
    }

    return (
        <Card className="p-5">
            <div className="flex items-center justify-between mb-1">
                <h2 className="text-lg font-bold text-card-foreground">Appliance Usage Dashboard</h2>
                <Button onClick={fetchApplianceData} size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                </Button>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
                Tracking {applianceData.length} appliance{applianceData.length !== 1 ? 's' : ''} for {selectedDataset || "shared-demo-user"} • Showing {filteredData.length} record{filteredData.length !== 1 ? 's' : ''}
            </p>

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
