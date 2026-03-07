import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const ApplianceUsageForm = () => {
    const [formData, setFormData] = useState({
        date: "",
        hours: "",
        applianceName: ""
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        
        try {
            // Step 1: Save to backend database
            const response = await fetch('http://localhost:3001/api/appliances', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to save appliance data');
            }
            
            const data = await response.json();
            
            // Step 2: Send to AI service for processing and Pinecone storage
            try {
                const aiResponse = await fetch('http://localhost:5001/api/ai/appliance-consumption', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        appliance_name: formData.applianceName,
                        hours: parseInt(formData.hours),
                        date: formData.date
                    })
                });
                
                if (aiResponse.ok) {
                    const aiData = await aiResponse.json();
                    console.log('AI processing result:', aiData);
                }
            } catch (aiError) {
                // Don't fail the whole operation if AI service is down
                console.warn('AI service unavailable:', aiError);
            }
            
            toast({
                title: "Success!",
                description: "Appliance usage saved successfully. Recommendations will be updated.",
            });
            
            // Reset the form
            setFormData({date:"", hours:"", applianceName:""});
            
            // Trigger a page refresh event so Recommendations component can reload
            window.dispatchEvent(new CustomEvent('appliance-added'));
        } catch (error) {
            console.error('Error submitting form:', error);
            toast({
                title: "Error",
                description: "Failed to save appliance data. Please try again.",
                variant: "destructive",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="p-5">
            <h2 className="text-lg font-bold text-card-foreground">Appliance Usage</h2>
            <p className="text-sm text-muted-foreground mb-4">
                Track how much energy your appliances use
            </p>
            
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Date of Usage */}
                <div className="space-y-2">
                    <Label htmlFor="date">Date of Usage</Label>
                    <Input
                        id="date"
                        type="date"
                        value={formData.date}
                        onChange={(e) => setFormData({...formData, date: e.target.value})}
                        required
                    />
                </div>

                {/* Number of Hours */}
                <div className="space-y-2">
                    <Label htmlFor="hours">Number of Hours</Label>
                    <Select
                        value={formData.hours}
                        onValueChange={(value) => setFormData({...formData, hours: value})}
                        required
                    >
                        <SelectTrigger id="hours">
                            <SelectValue placeholder="Select hours" />
                        </SelectTrigger>
                        <SelectContent>
                            {Array.from({ length: 24 }, (_, i) => i + 1).map((hour) => (
                                <SelectItem key={hour} value={hour.toString()}>
                                    {hour} {hour === 1 ? "hour" : "hours"}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Appliance Name */}
                <div className="space-y-2">
                    <Label htmlFor="appliance">Appliance Name</Label>
                    <Input
                        id="appliance"
                        type="text"
                        placeholder="e.g., Washing Machine"
                        value={formData.applianceName}
                        onChange={(e) => setFormData({...formData, applianceName: e.target.value})}
                        required
                    />
                </div>

                {/* Submit Button */}
                <Button type="submit" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Add Appliance"}
                </Button>
            </form>
        </Card>
    );
};

export default ApplianceUsageForm;