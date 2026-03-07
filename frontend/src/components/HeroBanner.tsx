import heroBg from "@/assets/hero-bg.jpg";
import { Zap, TrendingDown } from "lucide-react";

const HeroBanner = () => {
  return (
    <div className="relative overflow-hidden rounded-xl mb-6">
      <img
        src={heroBg}
        alt="Energy landscape"
        className="w-full h-48 md:h-56 object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary/40 flex items-center">
        <div className="px-6 md:px-10">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-6 w-6 text-accent" />
            <span className="text-primary-foreground/80 text-sm font-medium uppercase tracking-wider">
              GridSmart Energy
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-primary-foreground mb-1">
            Your Energy Dashboard
          </h1>
          <p className="text-primary-foreground/80 text-sm md:text-base max-w-lg">
            Understand your usage, shift to off-peak, save money — and help stabilise the grid.
          </p>
          <div className="flex items-center gap-1 mt-3 text-off-peak font-semibold text-sm">
            <TrendingDown className="h-4 w-4" />
            You're using 18% less during peak than last month!
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroBanner;
