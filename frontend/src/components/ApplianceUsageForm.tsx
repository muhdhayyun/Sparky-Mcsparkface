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

const ApplianceUsageForm = () => {
    const [formData, setFormData] = useState({
        date: "",
        hours: "",
        applianceName: ""
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log("Form submitted:", formData);
        // Add your form submission logic here

        // reset the form
        setFormData({date:"",hours:"",applianceName:""});
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
                <Button type="submit" className="w-full">
                    Add Appliance
                </Button>
            </form>
        </Card>
    );
};

export default ApplianceUsageForm;