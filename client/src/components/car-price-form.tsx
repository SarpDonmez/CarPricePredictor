import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { carPredictionSchema, type CarPrediction, type PredictionResult } from "@shared/schema";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Edit, Loader2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useEffect } from "react";

interface CarPriceFormProps {
  onPrediction: (result: PredictionResult, input: CarPrediction) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export default function CarPriceForm({ onPrediction, isLoading, setIsLoading }: CarPriceFormProps) {
  const { toast } = useToast();

  const form = useForm<CarPrediction>({
    resolver: zodResolver(carPredictionSchema),
    defaultValues: {
      year: 2018,
      mileage: 45000,
      mileageUnit: "miles",
      make: "",
      model: "",
      location: "US",
      currency: "USD",
      accidentHistory: "None",
      condition: "Good",
    },
  });

  // Fetch available makes
  const { data: makes = [] } = useQuery<string[]>({
    queryKey: ["/api/makes"],
  });

  // Watch form values to trigger model fetch
  const selectedMake = form.watch("make");
  const selectedYear = form.watch("year");

  // Fetch available models based on selected make and year
  const { data: models = [], isLoading: modelsLoading } = useQuery<string[]>({
    queryKey: ["/api/models", selectedMake, selectedYear],
    queryFn: async () => {
      if (!selectedMake || !selectedYear) return [];
      const response = await fetch(`/api/models?make=${encodeURIComponent(selectedMake)}&year=${selectedYear}`);
      if (!response.ok) throw new Error('Failed to fetch models');
      return response.json();
    },
    enabled: !!(selectedMake && selectedYear),
  });

  // Reset model field when make or year changes
  useEffect(() => {
    if (selectedMake && selectedYear) {
      form.setValue("model", "");
    }
  }, [selectedMake, selectedYear, form]);

  const predictMutation = useMutation({
    mutationFn: async (data: CarPrediction) => {
      const response = await apiRequest("POST", "/api/predict", data);
      return response.json();
    },
    onSuccess: (result: PredictionResult) => {
      const inputData = form.getValues();
      onPrediction(result, inputData);
      setIsLoading(false);
      toast({
        title: "Estimate Generated",
        description: "Your car price estimate is ready!",
      });
    },
    onError: (error: Error) => {
      setIsLoading(false);
      // Check if it's a validation error about car model/year combination
      const isValidationError = error.message && (
        error.message.includes("first produced") || 
        error.message.includes("discontinued") || 
        error.message.includes("not available")
      );
      
      toast({
        title: isValidationError ? "Invalid Car Information" : "Estimation Failed",
        description: error.message || "Failed to get price estimate. Please try again.",
        variant: "destructive",
        duration: isValidationError ? 8000 : 5000, // Show validation errors longer
      });
    },
  });

  const onSubmit = async (data: CarPrediction) => {
    setIsLoading(true);
    predictMutation.mutate(data);
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Edit className="h-4 w-4 text-primary" />
          <h3 className="text-lg font-semibold text-foreground" data-testid="text-form-title">
            Enter Car Details
          </h3>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" data-testid="form-car-prediction">
            {/* Year Input */}
            <FormField
              control={form.control}
              name="year"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Year</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1990}
                      max={2024}
                      placeholder="2018"
                      data-testid="input-year"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                    />
                  </FormControl>
                  <p className="text-xs text-muted-foreground">Enter year between 1990-2024</p>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Mileage Input with Unit Selection */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="mileage"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Odometer Reading</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={0}
                        placeholder="45000"
                        data-testid="input-mileage"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="mileageUnit"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Distance Unit</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-mileage-unit">
                          <SelectValue placeholder="Select unit..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="miles" data-testid="option-unit-miles">
                          🇺🇸 Miles
                        </SelectItem>
                        <SelectItem value="km" data-testid="option-unit-km">
                          🌍 Kilometers
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Current odometer reading on your vehicle
            </p>

            {/* Make Dropdown */}
            <FormField
              control={form.control}
              name="make"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Make</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger data-testid="select-make">
                        <SelectValue placeholder="Select make..." />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {makes.map((make: string) => (
                        <SelectItem key={make} value={make} data-testid={`option-make-${make}`}>
                          {make}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Model Dropdown */}
            <FormField
              control={form.control}
              name="model"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Model</FormLabel>
                  <Select 
                    onValueChange={field.onChange} 
                    value={field.value}
                    disabled={!selectedMake || !selectedYear || modelsLoading}
                  >
                    <FormControl>
                      <SelectTrigger data-testid="select-model">
                        <SelectValue 
                          placeholder={
                            !selectedMake || !selectedYear 
                              ? "Select make and year first" 
                              : modelsLoading 
                                ? "Loading models..." 
                                : models.length === 0 
                                  ? "No models available" 
                                  : "Select model..."
                          } 
                        />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {models.map((model: string) => (
                        <SelectItem key={model} value={model} data-testid={`option-model-${model}`}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    {!selectedMake || !selectedYear 
                      ? "Choose a make and year to see available models" 
                      : `Available models for ${selectedYear} ${selectedMake}`
                    }
                  </p>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Location and Currency Selection */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="location"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Location</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-location">
                          <SelectValue placeholder="Select location..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="US" data-testid="option-location-US">
                          🇺🇸 United States
                        </SelectItem>
                        <SelectItem value="Canada" data-testid="option-location-Canada">
                          🇨🇦 Canada
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Currency</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-currency">
                          <SelectValue placeholder="Select currency..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="USD" data-testid="option-currency-USD">
                          💵 USD - US Dollar
                        </SelectItem>
                        <SelectItem value="CAD" data-testid="option-currency-CAD">
                          🍁 CAD - Canadian Dollar
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Prices will be adjusted based on regional market conditions and converted to your selected currency
            </p>

            {/* Accident History and Condition */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="accidentHistory"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Accident History</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-accident-history">
                          <SelectValue placeholder="Select accident history..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="None" data-testid="option-accident-none">
                          ✅ No Accidents
                        </SelectItem>
                        <SelectItem value="Minor (1-2)" data-testid="option-accident-minor">
                          ⚠️ Minor (1-2)
                        </SelectItem>
                        <SelectItem value="Major (3+)" data-testid="option-accident-major">
                          🚨 Major (3+)
                        </SelectItem>
                        <SelectItem value="Serious/Total Loss" data-testid="option-accident-serious">
                          💥 Serious/Total Loss
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="condition"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Vehicle Condition</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger data-testid="select-condition">
                          <SelectValue placeholder="Select condition..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Excellent" data-testid="option-condition-excellent">
                          ⭐ Excellent
                        </SelectItem>
                        <SelectItem value="Good" data-testid="option-condition-good">
                          👍 Good
                        </SelectItem>
                        <SelectItem value="Fair" data-testid="option-condition-fair">
                          👌 Fair
                        </SelectItem>
                        <SelectItem value="Poor" data-testid="option-condition-poor">
                          👎 Poor
                        </SelectItem>
                        <SelectItem value="Parts only/Salvage" data-testid="option-condition-salvage">
                          🔧 Parts only/Salvage
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Vehicle condition and accident history significantly impact market value
            </p>

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full"
              disabled={isLoading}
              data-testid="button-estimate"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Get Price Estimate"
              )}
            </Button>
          </form>
        </Form>

        {/* Error Display */}
        {predictMutation.isError && (
          <Alert variant="destructive" className="mt-4" data-testid="alert-error">
            <AlertDescription>
              {predictMutation.error?.message || "Something went wrong. Please try again."}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
