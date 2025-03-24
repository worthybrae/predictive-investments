import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { LineChart, BarChart3, Search, TrendingUp, DollarSign, CheckCircle } from 'lucide-react';

export type PredictionStatus = 'pending' | 'analyzing' | 'researching' | 'finding_tickers' | 'creating_strategy' | 'completed' | 'failed';

interface StatusTrackerProps {
  status: PredictionStatus;
  progress: number;
  message: string;
}

const StatusTracker: React.FC<StatusTrackerProps> = ({
  status,
  progress,
  message
}) => {
  const steps = [
    { id: 'pending', label: 'Queued', icon: <LineChart className="h-5 w-5" /> },
    { id: 'analyzing', label: 'Analyzing', icon: <BarChart3 className="h-5 w-5" /> },
    { id: 'researching', label: 'Researching', icon: <Search className="h-5 w-5" /> },
    { id: 'finding_tickers', label: 'Finding Tickers', icon: <TrendingUp className="h-5 w-5" /> },
    { id: 'creating_strategy', label: 'Creating Strategy', icon: <DollarSign className="h-5 w-5" /> },
    { id: 'completed', label: 'Completed', icon: <CheckCircle className="h-5 w-5" /> }
  ];
  
  const currentStepIndex = steps.findIndex(step => step.id === status);
  
  return (
    <div className="max-w-3xl mx-auto mb-8">
      {/* Progress Steps */}
      <div className="mb-6">
        <div className="hidden md:flex items-center justify-between bg-white rounded-lg p-6 border shadow-sm">
          {steps.map((step, index) => {
            const isActive = index <= currentStepIndex;
            const isCurrentStep = step.id === status;
            
            return (
              <React.Fragment key={step.id}>
                {/* Step circle */}
                <div className="flex flex-col items-center">
                  <div 
                    className={`flex items-center justify-center w-10 h-10 rounded-full ${
                      isActive 
                        ? 'bg-primary text-primary-foreground shadow' 
                        : 'bg-muted/30 text-muted-foreground border'
                    } ${
                      isCurrentStep ? 'ring-2 ring-primary/20 animate-pulse' : ''
                    }`}
                  >
                    {step.icon}
                  </div>
                  <span className={`mt-2 text-xs font-medium ${isActive ? 'text-primary' : 'text-muted-foreground'}`}>
                    {step.label}
                  </span>
                </div>
                
                {/* Connector line (except after last step) */}
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-2 ${
                    index < currentStepIndex ? 'bg-primary' : 'bg-muted/30'
                  }`}></div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Mobile Steps (simpler version) */}
        <div className="md:hidden bg-white rounded-lg p-4 border shadow-sm">
          <div className="flex items-center mb-4">
            {steps.map((step, index) => {
              const isActive = index <= currentStepIndex;
              return (
                <div 
                  key={step.id}
                  className={`h-1 flex-1 ${index === 0 ? 'rounded-l-full' : ''} ${
                    index === steps.length - 1 ? 'rounded-r-full' : ''
                  } ${isActive ? 'bg-primary' : 'bg-muted/30'}`} 
                />
              );
            })}
          </div>
          <div className="flex items-center gap-2">
            <div 
              className="flex items-center justify-center w-10 h-10 rounded-full bg-primary text-primary-foreground shadow animate-pulse"
            >
              {steps[currentStepIndex]?.icon}
            </div>
            <div>
              <p className="font-medium">{steps[currentStepIndex]?.label}</p>
              <p className="text-xs text-muted-foreground">Step {currentStepIndex + 1} of {steps.length}</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Status Card */}
      <Card className="border shadow-md overflow-hidden">
        <CardHeader className="pb-3 bg-white border-b">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <span className="inline-block w-3 h-3 rounded-full bg-primary animate-pulse mr-2"></span>
              <h3 className="font-medium text-lg capitalize">
                {status === 'pending' ? 'Processing Queue' : status.replace('_', ' ')}
              </h3>
            </div>
            <Badge variant="outline" className="font-mono">{Math.round(progress)}%</Badge>
          </div>
        </CardHeader>
        <CardContent className="pb-6 pt-4">
          <Progress value={progress} className="h-2 mb-4" />
          <p className="text-sm text-muted-foreground">{message}</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default StatusTracker;