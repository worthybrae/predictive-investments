# api/services/prediction_queue.py
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, Any, List

from models.predictions import PredictionStatus, PredictionStatusResponse
from services.ai import AIService

class PredictionQueueManager:
    """Manager for asynchronous prediction processing."""
    
    # Store prediction statuses in memory (could be moved to database)
    _predictions: Dict[str, PredictionStatusResponse] = {}
    
    @classmethod
    def create_prediction(
        cls,
        prediction_text: str,
        options: Dict[str, Any] = None
    ) -> str:
        """
        Create a new prediction task and return its ID.
        
        Args:
            prediction_text: The prediction to analyze
            options: Optional parameters for prediction processing
            
        Returns:
            Prediction ID
        """
        prediction_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Initialize prediction status
        cls._predictions[prediction_id] = PredictionStatusResponse(
            prediction_id=prediction_id,
            status=PredictionStatus.PENDING,
            created_at=now,
            updated_at=now,
            message="Prediction queued for processing",
            progress=0.0,
            result=None
        )
        
        # Start processing in background
        asyncio.create_task(cls._process_prediction(prediction_id, prediction_text, options or {}))
        
        return prediction_id
    
    @classmethod
    def get_prediction_status(cls, prediction_id: str) -> Optional[PredictionStatusResponse]:
        """
        Get the current status of a prediction.
        
        Args:
            prediction_id: The prediction ID
            
        Returns:
            Current prediction status or None if not found
        """
        return cls._predictions.get(prediction_id)
    
    @classmethod
    def list_predictions(cls, limit: int = 10) -> List[PredictionStatusResponse]:
        """
        List recent predictions.
        
        Args:
            limit: Maximum number of predictions to return
            
        Returns:
            List of prediction statuses
        """
        # Sort by created_at (newest first) and limit
        return sorted(
            cls._predictions.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]
    
    @classmethod
    async def _process_prediction(
        cls,
        prediction_id: str,
        prediction_text: str,
        options: Dict[str, Any]
    ) -> None:
        """
        Process a prediction asynchronously.
        
        Args:
            prediction_id: The prediction ID
            prediction_text: The prediction text
            options: Processing options
        """
        try:
            # Extract options
            model = options.get("model", "gpt-4o-mini")
            use_web_search = options.get("use_web_search", False)
            search_model = options.get("search_model", "sonar")
            use_finviz_screener = options.get("use_finviz_screener", True)
            include_stock_data = options.get("include_stock_data", False)
            include_year_data = options.get("include_year_data", False)
            include_week_data = options.get("include_week_data", False)
            
            # 1. Analyze prediction
            cls._update_status(
                prediction_id,
                PredictionStatus.ANALYZING,
                "Analyzing prediction text",
                10.0
            )
            
            analysis_result = await AIService.analyze_prediction(
                prediction_text=prediction_text,
                model=model
            )
            
            if not analysis_result["success"]:
                raise Exception(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
            
            prediction_analysis = analysis_result["result"]
            
            # 2. Get market research (if requested)
            market_research = None
            if use_web_search:
                cls._update_status(
                    prediction_id,
                    PredictionStatus.RESEARCHING,
                    "Gathering market research",
                    30.0
                )
                
                perplexity_result = await AIService.get_market_research(
                    prediction_text=prediction_text,
                    industries=prediction_analysis.get("related_industries", []),
                    timeframe=prediction_analysis.get("timing", ""),
                    search_model=search_model
                )
                
                if perplexity_result["success"]:
                    market_research = perplexity_result["content"]
            
            # 3. Find relevant tickers
            cls._update_status(
                prediction_id,
                PredictionStatus.FINDING_TICKERS,
                "Finding relevant tickers",
                50.0
            )
            
            tickers_result = await AIService.find_relevant_tickers(
                prediction_text=prediction_text,
                prediction_analysis=prediction_analysis,
                use_web_search=use_web_search,
                search_model=search_model,
                model=model
            )
            
            if not tickers_result["success"]:
                raise Exception(f"Ticker search failed: {tickers_result.get('error', 'Unknown error')}")
            
            relevant_tickers = tickers_result["result"]
            
            # 4. Create investment strategy
            cls._update_status(
                prediction_id,
                PredictionStatus.CREATING_STRATEGY,
                "Creating investment strategy",
                70.0
            )
            
            strategy_result = await AIService.create_investment_strategy(
                prediction_text=prediction_text,
                prediction_analysis=prediction_analysis,
                relevant_tickers=relevant_tickers,
                market_research=market_research,
                include_stock_data=include_stock_data,
                include_year_data=include_year_data,
                include_week_data=include_week_data,
                model=model
            )
            
            if not strategy_result["success"]:
                raise Exception(f"Strategy creation failed: {strategy_result.get('error', 'Unknown error')}")
            
            investment_strategy = strategy_result["result"]
            
            # 5. Compile final results
            result = {
                "prediction_text": prediction_text,
                "success": True,
                "analysis": prediction_analysis,
                "market_research": market_research,
                "relevant_tickers": relevant_tickers,
                "investment_strategy": investment_strategy
            }
            
            # Update status to completed
            cls._update_status(
                prediction_id,
                PredictionStatus.COMPLETED,
                "Prediction analysis completed",
                100.0,
                result
            )
            
        except Exception as e:
            # Handle any errors
            cls._update_status(
                prediction_id,
                PredictionStatus.FAILED,
                f"Prediction processing failed: {str(e)}",
                100.0
            )
    
    @classmethod
    def _update_status(
        cls,
        prediction_id: str,
        status: PredictionStatus,
        message: str,
        progress: float,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the status of a prediction.
        
        Args:
            prediction_id: The prediction ID
            status: New status
            message: Status message
            progress: Progress percentage (0-100)
            result: Optional prediction results
        """
        if prediction_id in cls._predictions:
            prediction = cls._predictions[prediction_id]
            prediction.status = status
            prediction.message = message
            prediction.progress = progress
            prediction.updated_at = datetime.now()
            
            if result is not None:
                prediction.result = result