from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
import requests
from concurrent import futures
from django.conf import settings
import logging

from .calculations import calculate_execution_time, calculate_received_rows

logger = logging.getLogger(__name__)

GO_SERVICE_URL_BASE = 'http://127.0.0.1:8080'
SECRET_KEY = "SuperSecretKey"

executor = futures.ThreadPoolExecutor(max_workers=5)


def calculate_and_prepare_result(query_id, indexes_data):
    """
    Performs async calculation with 5-10 second delay.
    
    Args:
        query_id: int - Query ID
        indexes_data: List[dict] - Index query data
        
    Returns:
        dict with calculation results
    """
    print(f"Starting calculation for query ID: {query_id}...")
    time.sleep(7)  # 5-10 second delay
    
    # Calculate execution time
    execution_time = calculate_execution_time(indexes_data)
    
    # Calculate received rows for each index
    results = []
    for index_data in indexes_data:
        try:
            received_rows = calculate_received_rows(
                index_data.get('cardinality', 0),
                index_data.get('date_query', ''),
                index_data.get('rows_count', 0)
            )
            results.append({
                'index_id': index_data.get('received_rows_id'),
                'received_rows': received_rows,
                'success': True
            })
        except ValueError as e:
            logger.error(f"Calculation error for index: {str(e)}")
            results.append({
                'index_id': index_data.get('received_rows_id'),
                'received_rows': 0,
                'success': False,
                'error': str(e)
            })
    
    print(f"Finished calculation for query ID: {query_id}. Execution time: {execution_time}")
    
    return {
        'query_id': query_id,
        'execution_time': execution_time,
        'index_results': results,
        'timestamp': time.time()
    }


def send_single_result_callback(task):
    """
    Callback triggered when calculation task is done.
    Sends results back to main Go service.
    """
    try:
        result = task.result()
        query_id = result['query_id']
        print(f"Callback triggered for query ID: {query_id}")
    except Exception as e:
        print(f"An error occurred in the background task: {e}")
        logger.error(f"Background task error: {e}")
        return
    
    callback_url = f"{GO_SERVICE_URL_BASE}/api/v1/queries/{result['query_id']}/results"
    
    payload = {
        'query_id': result['query_id'],
        'execution_time': result['execution_time'],
        'index_results': result['index_results'],
        'timestamp': result['timestamp']
    }
    
    headers = {
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(callback_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Successfully sent results for query {query_id}. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send result for query {query_id}: {e}")
        logger.error(f"Failed to send results: {e}")


@api_view(['POST'])
def calculate(request):
    """
    Process calculation request asynchronously.
    
    Expected payload:
    {
        "query_id": 1,
        "indexes_data": [
            {
                "index_id": 1,
                "cardinality": 100,
                "rows_count": 500,
                "date_query": "2024-12-15",
                "received_rows_id": 1
            }
        ]
    }
    
    Returns 202 Accepted
    """
    if "query_id" not in request.data or "indexes_data" not in request.data:
        return Response(
            {"error": "Missing 'query_id' or 'indexes_data'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    query_id = request.data["query_id"]
    indexes_data = request.data["indexes_data"]
    
    print(f"Accepted task for query ID: {query_id} with {len(indexes_data)} indexes.")
    
    # Submit task to thread pool
    task = executor.submit(calculate_and_prepare_result, query_id, indexes_data)
    task.add_done_callback(send_single_result_callback)
    
    return Response(
        {
            "message": f"Calculation for query ID {query_id} accepted. Processing in background.",
            "query_id": query_id,
            "estimated_time": "5-10 seconds"
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'async-calculator'
    })
