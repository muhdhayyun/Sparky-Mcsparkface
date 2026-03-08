import HeroBanner from "@/components/HeroBanner";
import PeakAlert from "@/components/PeakAlert";
import ImpactCards from "@/components/ImpactCards";
import UsageChart from "@/components/UsageChart";
import WeeklyOverview from "@/components/WeeklyOverview";
import Recommendations from "@/components/Recommendations";
import CommunityImpact from "@/components/CommunityImpact";
import ApplianceUsageForm from "@/components/ApplianceUsageForm";
import ApplianceUsageDashboard from "@/components/ApplianceUsageDashboard";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useEffect, useState } from "react";

interface DatasetOption {
  id: string;
  filename: string;
  label: string;
}

const Index = () => {
  const [datasets, setDatasets] = useState<DatasetOption[]>([]);
  const [selectedDataset, setSelectedDataset] = useState("");

  const selectedDatasetIndex = datasets.findIndex((dataset) => dataset.id === selectedDataset);
  const selectedUserLabel = selectedDatasetIndex >= 0
    ? `User ${String(selectedDatasetIndex + 1).padStart(2, "0")}`
    : "User";

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const response = await fetch("http://localhost:5001/api/ai/datasets");
        if (!response.ok) {
          throw new Error("Failed to load datasets");
        }

        const data = await response.json();
        const loadedDatasets = data.datasets ?? [];
        setDatasets(loadedDatasets);

        if (loadedDatasets.length > 0) {
          setSelectedDataset(loadedDatasets[0].id);
        }
      } catch (error) {
        console.error("Error loading datasets:", error);
      }
    };

    fetchDatasets();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-4 py-6">
        <HeroBanner />
        {/* <PeakAlert />
        <ImpactCards /> */}

        <div className="grid md:grid-cols-2 gap-4 mt-4">
          <UsageChart selectedDataset={selectedDataset} selectedUserLabel={selectedUserLabel} />
          <WeeklyOverview selectedDataset={selectedDataset} selectedUserLabel={selectedUserLabel} />
        </div>

        <Card className="mt-4 p-4">
          <div className="space-y-2">
            <Label htmlFor="dataset-selector">Simple Login</Label>
            <Select value={selectedDataset} onValueChange={setSelectedDataset}>
              <SelectTrigger id="dataset-selector" className="max-w-md">
                <SelectValue placeholder="Select a user" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((dataset, index) => (
                  <SelectItem key={dataset.id} value={dataset.id}>
                    {`User ${String(index + 1).padStart(2, "0")} (${dataset.label})`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Switch between demo users. Each user is currently mapped to one electricity dataset.
            </p>
          </div>
        </Card>

        <div className="grid md:grid-cols-5 gap-4 mt-4">
          <div className="md:col-span-3">
            <Recommendations selectedDataset={selectedDataset} />
          </div>
          <div className="md:col-span-2">
            <div>
              <CommunityImpact />
            </div>
            <div className="mt-4">
              <ApplianceUsageForm selectedDataset={selectedDataset} />
            </div>
          </div>
        </div>

        <div className="max-w-5xl mx-auto mt-4">
          <ApplianceUsageDashboard selectedDataset={selectedDataset} />
        </div>

        <footer className="text-center text-xs text-muted-foreground mt-10 pb-6">
          SP Energy © 2026 — Helping you use energy smarter.
        </footer>
      </div>
    </div>
  );
};

export default Index;
