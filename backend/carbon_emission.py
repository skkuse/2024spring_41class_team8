def calculate_carbon_emissions(execution_time, memory_usage, tdp_per_core=16, num_cores=4, pue=1.2, carbon_intensity=0.5, memory_power_consumption=0.000488):
    """
    탄소 배출량을 계산합니다.

    Args:
        execution_time (float): 실행 시간 (초)
        memory_usage (float): 메모리 사용량 (MB)
        tdp_per_core (float): 코어당 TDP (W)
        num_cores (int): 코어 수
        pue (float): Power Usage Effectiveness
        carbon_intensity (float): 탄소 집약도 (kg CO2e/kWh)
        memory_power_consumption (float): 메모리 전력 소비 (W/MB)

    Returns:
        float: 탄소 배출량 (kg CO2e)
    """
    total_tdp = tdp_per_core * num_cores  # 총 전력 소비량 (W)
    memory_power = memory_usage * memory_power_consumption  # 메모리 전력 소비량 (W)
    total_power_consumption = total_tdp + memory_power  # 총 전력 소비량 (W)
    
    energy_consumed = total_power_consumption * (execution_time / 3600) * pue  # kWh, PUE 적용
    carbon_emissions = energy_consumed * carbon_intensity  # kg CO2e
    return carbon_emissions