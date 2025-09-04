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
      make: "",
      model: "",
    },
  });

  // Fetch available makes
  const { data: makes = [] } = useQuery({
    queryKey: ["/api/makes"],
  });

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
      toast({
        title: "Estimation Failed",
        description: error.message || "Failed to get price estimate. Please try again.",
        variant: "destructive",
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

            {/* Mileage Input */}
            <FormField
              control={form.control}
              name="mileage"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Mileage</FormLabel>
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
                  <p className="text-xs text-muted-foreground">Current odometer reading in miles</p>
                  <FormMessage />
                </FormItem>
              )}
            />

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

            {/* Model Input */}
            <FormField
              control={form.control}
              name="model"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Model</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., Camry, Civic, F-150"
                      data-testid="input-model"
                      {...field}
                    />
                  </FormControl>
                  <p className="text-xs text-muted-foreground">Enter the specific model name</p>
                  <FormMessage />
                </FormItem>
              )}
            />

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
