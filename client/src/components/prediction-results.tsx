import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calculator, TrendingUp, Download, RotateCcw, CheckCircle, Loader2 } from "lucide-react";
import { type PredictionResult } from "@shared/schema";

interface PredictionResultsProps {
  prediction: PredictionResult | null;
  inputData: {year: number; mileage: number; make: string; model: string; location: string; currency: string} | null;
  isLoading: boolean;
  onReset: () => void;
}

export default function PredictionResults({ prediction, inputData, isLoading, onReset }: PredictionResultsProps) {
  const formatPrice = (price: number, currency?: string) => {
    const currencyCode = currency || prediction?.currency || 'USD';
    const locale = currencyCode === 'CAD' ? 'en-CA' : 'en-US';
    
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatMileage = (mileage: number) => {
    return new Intl.NumberFormat('en-US').format(mileage);
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <TrendingUp className="h-4 w-4 text-primary" />
          <h3 className="text-lg font-semibold text-foreground" data-testid="text-results-title">
            Price Estimate
          </h3>
        </div>

        {/* Default State */}
        {!prediction && !isLoading && (
          <div className="text-center py-12" data-testid="state-default">
            <div className="bg-muted/50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calculator className="h-8 w-8 text-muted-foreground" />
            </div>
            <h4 className="text-lg font-medium text-foreground mb-2">Ready to Estimate</h4>
            <p className="text-muted-foreground">
              Fill out the form to get an instant price estimate for your vehicle.
            </p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12" data-testid="state-loading">
            <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Loader2 className="h-8 w-8 text-primary animate-spin" />
            </div>
            <h4 className="text-lg font-medium text-foreground mb-2">Analyzing...</h4>
            <p className="text-muted-foreground">
              Our AI model is processing your vehicle details.
            </p>
          </div>
        )}

        {/* Results State */}
        {prediction && !isLoading && (
          <div className="animate-in slide-in-from-bottom-4 duration-500" data-testid="state-results">
            {/* Main Estimate */}
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-primary to-purple-600 p-6 rounded-lg text-white mb-4">
                <h4 className="text-sm font-medium opacity-90 mb-1">Estimated Value</h4>
                <div className="text-4xl font-bold" data-testid="text-estimated-price">
                  {formatPrice(prediction.estimated_price)}
                </div>
                <p className="text-sm opacity-90 mt-1">
                  Based on {prediction.location === 'Canada' ? 'Canadian' : 'US'} market data
                </p>
              </div>
              
              {/* Confidence Indicator */}
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span data-testid="text-confidence">
                  {prediction.confidence === 'high' ? 'High' : 
                   prediction.confidence === 'medium' ? 'Medium' : 'Low'} confidence estimate
                </span>
              </div>
            </div>

            {/* Car Summary */}
            {inputData && (
              <div className="bg-muted/30 rounded-lg p-4 mb-6" data-testid="section-vehicle-summary">
                <h5 className="font-medium text-foreground mb-3">Vehicle Summary</h5>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Year:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-year">
                      {inputData.year}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Mileage:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-mileage">
                      {formatMileage(inputData.mileage)} mi
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Make:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-make">
                      {inputData.make}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Model:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-model">
                      {inputData.model}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Location:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-location">
                      {inputData.location === 'Canada' ? '🇨🇦 Canada' : '🇺🇸 United States'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Currency:</span>
                    <span className="font-medium text-foreground" data-testid="text-summary-currency">
                      {inputData.currency === 'CAD' ? '🍁 CAD' : '💵 USD'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Price Range */}
            <div className="border border-border rounded-lg p-4 mb-6" data-testid="section-price-range">
              <h5 className="font-medium text-foreground mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" />
                Expected Price Range
              </h5>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Low Estimate</span>
                  <span className="font-medium text-foreground" data-testid="text-low-estimate">
                    {formatPrice(prediction.low_estimate)}
                  </span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: "75%" }}></div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">High Estimate</span>
                  <span className="font-medium text-foreground" data-testid="text-high-estimate">
                    {formatPrice(prediction.high_estimate)}
                  </span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button 
                variant="secondary" 
                className="w-full"
                data-testid="button-download-report"
              >
                <Download className="mr-2 h-4 w-4" />
                Download Report
              </Button>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={onReset}
                data-testid="button-new-estimate"
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                New Estimate
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
