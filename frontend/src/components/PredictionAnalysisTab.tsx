import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { LineChart, BarChart3, Calendar, ThermometerSun, ThermometerSnowflake } from 'lucide-react';

interface PredictionAnalysis {
  timing: string;
  confidence: number;
  tolerance: number;
  related_industries: string[];
  name: string;
  category: string;
  best_case_scenario: string;
  worst_case_scenario: string;
}

interface PredictionAnalysisTabProps {
  analysis: PredictionAnalysis;
}

const PredictionAnalysisTab: React.FC<PredictionAnalysisTabProps> = ({ 
  analysis 
}) => {
  const getCategoryColor = (category: string) => {
    const categories: Record<string, string> = {
      'technology': 'bg-blue-100 text-blue-800',
      'economic': 'bg-green-100 text-green-800',
      'political': 'bg-purple-100 text-purple-800',
      'financial': 'bg-amber-100 text-amber-800',
      'market': 'bg-emerald-100 text-emerald-800',
      'social': 'bg-pink-100 text-pink-800',
      'environmental': 'bg-teal-100 text-teal-800'
    };
    
    const lowerCategory = category.toLowerCase();
    
    // Find a match or partial match
    for (const [key, value] of Object.entries(categories)) {
      if (lowerCategory.includes(key)) {
        return value;
      }
    }
    
    // Default
    return 'bg-gray-100 text-gray-800';
  };
  
  const confidenceColor = analysis.confidence > 0.7 
    ? 'bg-green-600' 
    : analysis.confidence > 0.4 
    ? 'bg-amber-500' 
    : 'bg-red-500';
  
  return (
    <Card className="overflow-hidden border-t-4 border-t-primary shadow-md">
      <CardHeader className="pb-3 bg-gradient-to-r from-primary/10 to-transparent border-b">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div>
            <CardTitle className="text-xl md:text-2xl text-primary flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              {analysis.name}
            </CardTitle>
            <div className="mt-2 text-sm md:text-base flex items-center gap-2 flex-wrap">
              <span className={`px-2 py-1 rounded-full text-xs ${getCategoryColor(analysis.category)}`}>
                {analysis.category}
              </span>
              <span className="flex items-center gap-1 text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {analysis.timing}
              </span>
            </div>
          </div>
          <div className="flex gap-3 flex-wrap">
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className={`h-14 w-14 rounded-full ${confidenceColor} flex items-center justify-center text-white font-bold`}>
                  {Math.round(analysis.confidence * 10)}
                </div>
              </div>
              <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="16" fill="none" 
                  className="stroke-muted" strokeWidth="3"></circle>
                <circle cx="18" cy="18" r="16" fill="none" 
                  className="stroke-current text-primary" strokeWidth="3" 
                  strokeDasharray="100" 
                  strokeDashoffset={100 - Math.round(analysis.confidence * 100)}
                  strokeLinecap="round"></circle>
              </svg>
              <div className="absolute top-full left-0 right-0 text-center mt-1">
                <span className="text-xs text-muted-foreground">Confidence</span>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        <div>
          <h4 className="font-medium mb-3 text-primary flex items-center">
            <LineChart className="h-4 w-4 mr-2" />
            Related Industries
          </h4>
          <div className="flex flex-wrap gap-2">
            {analysis.related_industries.map((industry, i) => (
              <Badge key={i} variant="outline" className="px-3 py-1 text-sm bg-white hover:bg-primary/5 transition-colors border shadow-sm">
                {industry}
              </Badge>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:border-green-300 transition-all">
            <h4 className="font-medium mb-3 text-green-700 flex items-center">
              <ThermometerSun className="h-4 w-4 mr-2 text-green-500" />
              Best Case Scenario
            </h4>
            <div className="p-4 bg-green-50 border border-green-100 rounded-md">
              <p className="text-sm leading-relaxed">{analysis.best_case_scenario}</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border shadow-sm hover:border-red-300 transition-all">
            <h4 className="font-medium mb-3 text-red-700 flex items-center">
              <ThermometerSnowflake className="h-4 w-4 mr-2 text-red-500" />
              Worst Case Scenario
            </h4>
            <div className="p-4 bg-red-50 border border-red-100 rounded-md">
              <p className="text-sm leading-relaxed">{analysis.worst_case_scenario}</p>
            </div>
          </div>
        </div>
        
        <div>
          <h4 className="font-medium mb-3 text-primary flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Risk Tolerance
          </h4>
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <Progress value={analysis.tolerance * 100} className="h-3" 
              style={{
                background: 'linear-gradient(to right, #22c55e, #f97316, #ef4444)'
              }}
            />
            <div className="flex justify-between mt-3 text-xs text-muted-foreground">
              <span className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                Low Risk
              </span>
              <span className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-amber-500 mr-1"></div>
                Medium Risk
              </span>
              <span className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                High Risk  
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PredictionAnalysisTab;