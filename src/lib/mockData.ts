export interface UsagePoint {
  time: string;
  usage: number;
  isPeak: boolean;
}

export const generateDailyUsage = (): UsagePoint[] => {
  const data: UsagePoint[] = [];
  for (let h = 0; h < 24; h++) {
    for (let m = 0; m < 60; m += 30) {
      const time = `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}`;
      const isPeak = (h >= 7 && h < 9) || (h >= 17 && h < 21);
      let base = 0.3 + Math.random() * 0.4;
      if (isPeak) base += 0.8 + Math.random() * 1.2;
      if (h >= 22 || h < 6) base = 0.15 + Math.random() * 0.2;
      data.push({ time, usage: parseFloat(base.toFixed(2)), isPeak });
    }
  }
  return data;
};

export const weeklyUsage = [
  { day: "Mon", usage: 18.2, target: 16 },
  { day: "Tue", usage: 15.4, target: 16 },
  { day: "Wed", usage: 14.8, target: 16 },
  { day: "Thu", usage: 19.1, target: 16 },
  { day: "Fri", usage: 16.5, target: 16 },
  { day: "Sat", usage: 21.3, target: 16 },
  { day: "Sun", usage: 17.8, target: 16 },
];

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  savings: string;
  impact: "high" | "medium" | "low";
  icon: string;
}

export const recommendations: Recommendation[] = [
  {
    id: "1",
    title: "Shift laundry to off-peak",
    description: "Run your washing machine after 9 PM instead of during peak hours (5–9 PM). This reduces grid stress and your bill.",
    savings: "$4.20/week",
    impact: "high",
    icon: "washing-machine",
  },
  {
    id: "2",
    title: "Adjust AC by 2°C",
    description: "Raising your thermostat by just 2°C during peak hours can cut cooling costs significantly.",
    savings: "$6.50/week",
    impact: "high",
    icon: "thermometer",
  },
  {
    id: "3",
    title: "Use dishwasher at night",
    description: "Schedule your dishwasher to run after 10 PM to take advantage of lower off-peak rates.",
    savings: "$2.10/week",
    impact: "medium",
    icon: "utensils",
  },
  {
    id: "4",
    title: "Unplug standby devices",
    description: "Devices on standby can account for up to 10% of your bill. Unplug chargers and entertainment systems when not in use.",
    savings: "$3.00/week",
    impact: "medium",
    icon: "plug",
  },
  {
    id: "5",
    title: "Pre-cool your home",
    description: "Cool your home before 5 PM when rates are lower, then let it coast through peak hours.",
    savings: "$5.00/week",
    impact: "high",
    icon: "snowflake",
  },
];

export const impactStats = {
  monthlySavings: 48.6,
  carbonReduced: 32,
  peakReduction: 18,
  streak: 12,
  communityRank: 142,
  communityTotal: 5200,
};
