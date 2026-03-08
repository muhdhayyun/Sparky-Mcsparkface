import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Lightbulb,
  Check,
  Clock,
  AlertCircle,
  RefreshCw,
  Sparkles,
} from "lucide-react";

interface AIRecommendation {
  recommendations: string;
  appliance_count: number;
  based_on?: any[];
}

interface RecommendationsProps {
  selectedDataset: string;
}

interface ParsedRecommendationItem {
  title: string;
  description: string;
}

const Recommendations = ({ selectedDataset }: RecommendationsProps) => {
  const [recommendations, setRecommendations] = useState<AIRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState<Set<number>>(new Set());

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (selectedDataset) {
        params.set("dataset", selectedDataset);
      }

      const response = await fetch(`http://localhost:5001/api/ai/recommendations?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
      }
      
      const data = await response.json();
      setRecommendations(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load AI recommendations';
      setError(errorMsg);
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
    
    // Listen for appliance-added events to refresh recommendations
    const handleApplianceAdded = () => {
      fetchRecommendations();
    };
    
    window.addEventListener('appliance-added', handleApplianceAdded);
    
    return () => {
      window.removeEventListener('appliance-added', handleApplianceAdded);
    };
  }, [selectedDataset]);

  const toggle = (index: number) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      next.has(index) ? next.delete(index) : next.add(index);
      return next;
    });
  };

  const parseRecommendations = (text: string) => {
    // Split by numbered items (1., 2., etc.)
    const lines = text.split('\n');
    const peakHoursLine = lines.find(line => line.includes('Peak Grid Hours'));
    const analyzedLine = lines.find(line => line.includes('Analyzed'));
    
    const recItems: ParsedRecommendationItem[] = [];
    let currentItem = '';

    const parseItem = (itemText: string): ParsedRecommendationItem => {
      const cleaned = itemText.replace(/\*\*/g, '').trim();
      const [titlePart, ...rest] = cleaned.split(':');
      if (rest.length === 0) {
        return {
          title: cleaned,
          description: '',
        };
      }

      return {
        title: titlePart.trim(),
        description: rest.join(':').trim(),
      };
    };
    
    for (const line of lines) {
      // Check if line starts with a number followed by a period
      const match = line.match(/^\d+\.\s+(.+)/);
      if (match) {
        if (currentItem) {
          recItems.push(parseItem(currentItem));
        }
        currentItem = match[1];
      } else if (currentItem && line.trim() && !line.includes('**') && !line.includes('*Analyzed*')) {
        currentItem += ' ' + line.trim();
      }
    }
    
    if (currentItem) {
      recItems.push(parseItem(currentItem));
    }
    
    return {
      peakHours: peakHoursLine?.replace(/\*\*/g, '').replace('Peak Grid Hours (Based on Real Data):', '').trim() || null,
      analyzedInfo: analyzedLine?.replace(/\*/g, '').trim() || null,
      items: recItems,
    };
  };

  if (loading) {
    return (
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <Skeleton className="h-6 w-48 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-10 w-10 rounded-full" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-card-foreground">Smart Recommendations</h2>
            <p className="text-sm text-muted-foreground">AI-powered energy saving tips</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <AlertCircle className="h-12 w-12 text-destructive mb-3" />
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <p className="text-xs text-muted-foreground mb-4">
            Make sure the AI service is running on port 5001
          </p>
          <Button onClick={fetchRecommendations} size="sm" variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (!recommendations || !recommendations.recommendations) {
    return (
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-card-foreground">Smart Recommendations</h2>
            <p className="text-sm text-muted-foreground">No appliance data yet</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Lightbulb className="h-12 w-12 text-muted-foreground mb-3" />
          <p className="text-sm text-muted-foreground mb-2">
            Start tracking your appliances to get personalized recommendations!
          </p>
          <p className="text-xs text-muted-foreground">
            Add your first appliance using the form above.
          </p>
        </div>
      </Card>
    );
  }

  const parsed = parseRecommendations(recommendations.recommendations);
  const totalItems = parsed.items.length;

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-card-foreground">Smart Recommendations</h2>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
              <Sparkles className="h-3 w-3 mr-1" />
              AI-Powered
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            {completed.size}/{totalItems} actions taken • Based on {recommendations.appliance_count} appliances
          </p>
        </div>
        {/* progress ring */}
        <div className="relative h-10 w-10">
          <svg viewBox="0 0 36 36" className="h-10 w-10 -rotate-90">
            <circle
              cx="18" cy="18" r="15"
              fill="none"
              stroke="hsl(200, 25%, 93%)"
              strokeWidth="3"
            />
            <circle
              cx="18" cy="18" r="15"
              fill="none"
              stroke="hsl(168, 60%, 42%)"
              strokeWidth="3"
              strokeDasharray={`${totalItems > 0 ? (completed.size / totalItems) * 94.25 : 0} 94.25`}
              strokeLinecap="round"
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-card-foreground">
            {totalItems > 0 ? Math.round((completed.size / totalItems) * 100) : 0}%
          </span>
        </div>
      </div>

      {/* Peak Hours Info */}
      {parsed.peakHours && (
        <div className="mb-4 p-3 rounded-lg bg-peak/5 border border-peak/20">
          <div className="flex items-start gap-2">
            <Clock className="h-4 w-4 text-peak mt-0.5 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-peak mb-0.5">Peak Grid Hours</p>
              <p className="text-xs text-card-foreground font-medium">{parsed.peakHours}</p>
              {parsed.analyzedInfo && (
                <p className="text-[10px] text-muted-foreground mt-1">{parsed.analyzedInfo}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="mb-3">
        <Button 
          onClick={fetchRecommendations} 
          size="sm" 
          variant="outline" 
          className="w-full"
          disabled={loading}
        >
          <RefreshCw className={`h-3 w-3 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Recommendations
        </Button>
      </div>

      {/* Recommendations List */}
      <div className="space-y-3">
        {parsed.items.map((item, index) => {
          const done = completed.has(index);
          return (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                done
                  ? "bg-off-peak/5 border-off-peak/30"
                  : "bg-card border-border hover:border-primary/30"
              }`}
              onClick={() => toggle(index)}
            >
              <div className={`shrink-0 p-2 rounded-lg ${done ? "bg-off-peak/20 text-off-peak" : "bg-primary/10 text-primary"}`}>
                {done ? <Check className="h-4 w-4" /> : <Lightbulb className="h-4 w-4" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm leading-relaxed ${done ? "line-through text-muted-foreground" : "text-card-foreground"}`}>
                  <span className="font-semibold">{item.title}</span>
                  {item.description ? `: ${item.description}` : ''}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default Recommendations;
