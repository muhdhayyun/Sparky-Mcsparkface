import HeroBanner from "@/components/HeroBanner";
import PeakAlert from "@/components/PeakAlert";
import ImpactCards from "@/components/ImpactCards";
import UsageChart from "@/components/UsageChart";
import WeeklyOverview from "@/components/WeeklyOverview";
import Recommendations from "@/components/Recommendations";
import CommunityImpact from "@/components/CommunityImpact";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-4 py-6">
        <HeroBanner />
        <PeakAlert />
        <ImpactCards />

        <div className="grid md:grid-cols-2 gap-4 mt-4">
          <UsageChart />
          <WeeklyOverview />
        </div>

        <div className="grid md:grid-cols-5 gap-4 mt-4">
          <div className="md:col-span-3">
            <Recommendations />
          </div>
          <div className="md:col-span-2">
            <CommunityImpact />
          </div>
        </div>

        <footer className="text-center text-xs text-muted-foreground mt-10 pb-6">
          GridSmart Energy © 2026 — Helping you use energy smarter.
        </footer>
      </div>
    </div>
  );
};

export default Index;
