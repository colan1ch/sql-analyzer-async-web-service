import math
import logging

logger = logging.getLogger(__name__)


def calculate_execution_time(indexes_query_data):
    """
    Calculates execution time based on indexes query data.
    Formula: sum(log2(cardinality)) + product(rows_count / cardinality)
    
    Args:
        indexes_query_data: List of dicts with 'cardinality' and 'rows_count'
        
    Returns:
        float: Calculated execution time
    """
    if not indexes_query_data:
        return 0.0
        
    total_sum = 0.0
    product = 1.0
    
    for data in indexes_query_data:
        cardinality = data.get('cardinality', 1)
        rows_count = data.get('rows_count', 1)
        
        if cardinality <= 0:
            cardinality = 1
        if rows_count <= 0:
            rows_count = 1
            
        total_sum += math.log2(float(cardinality))
        product *= float(rows_count) / float(cardinality)
    
    result = float(total_sum + product)
    logger.info(f"Calculated execution_time: {result}")
    return result


def calculate_received_rows(cardinality, date_query, rows_count):
    """
    Calculates received rows count.
    Formula: rows_count - cardinality
    
    Args:
        cardinality: int - cardinality value
        date_query: str - query date (validation)
        rows_count: int - total rows count
        
    Returns:
        int: Calculated received rows
        
    Raises:
        ValueError: If date_query is empty
    """
    if not date_query:
        raise ValueError("неправильная дата запроса")
    
    result = rows_count - cardinality
    logger.info(f"Calculated received_rows: {result} (rows_count={rows_count}, cardinality={cardinality})")
    return max(0, result)
