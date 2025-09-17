class OptimizationEngine:
    """
    Energy optimization engine for household battery scheduling
    """
    
    def __init__(self):
        self.battery_capacity = 10.0  # kWh
        self.max_charge_rate = 3.0   # kW
        self.max_discharge_rate = 3.0  # kW
        self.efficiency = 0.95       # Battery efficiency
    
    def optimize_energy(self, household_data: list) -> list:
        """
        Optimize energy consumption and battery scheduling
        
        Args:
            household_data: List of household consumption data
            
        Returns:
            List of optimization schedules with charge/discharge values
        """
        if not household_data:
            return []
        
        # Enhanced optimization logic (replacing simple dummy logic)
        schedule = []
        current_battery_level = 5.0  # Start with 50% battery
        
        for data in household_data:
            consumption = data.get("consumption", 0.0)
            
            # Simple optimization strategy:
            # - Charge during low consumption periods
            # - Discharge during high consumption periods
            
            if consumption < 1.5:  # Low consumption - charge battery
                charge_amount = min(
                    self.max_charge_rate * 0.25,  # 15 min interval
                    self.battery_capacity - current_battery_level
                )
                discharge_amount = 0.0
                current_battery_level += charge_amount * self.efficiency
                
            elif consumption > 2.5:  # High consumption - discharge battery
                discharge_amount = min(
                    self.max_discharge_rate * 0.25,  # 15 min interval
                    current_battery_level
                )
                charge_amount = 0.0
                current_battery_level -= discharge_amount
                
            else:  # Normal consumption - no battery action
                charge_amount = 0.0
                discharge_amount = 0.0
            
            # Keep battery level within bounds
            current_battery_level = max(0.0, min(self.battery_capacity, current_battery_level))
            
            schedule.append({
                "charge": round(charge_amount, 3),
                "discharge": round(discharge_amount, 3),
                "battery_level": round(current_battery_level, 3),
                "consumption": consumption
            })
        
        return schedule
    
    def get_battery_status(self) -> dict:
        """Get current battery system status"""
        return {
            "capacity": self.battery_capacity,
            "max_charge_rate": self.max_charge_rate,
            "max_discharge_rate": self.max_discharge_rate,
            "efficiency": self.efficiency
        }
    
    def update_battery_config(self, capacity: float = None, charge_rate: float = None, 
                            discharge_rate: float = None, efficiency: float = None):
        """Update battery system configuration"""
        if capacity is not None:
            self.battery_capacity = capacity
        if charge_rate is not None:
            self.max_charge_rate = charge_rate
        if discharge_rate is not None:
            self.max_discharge_rate = discharge_rate
        if efficiency is not None:
            self.efficiency = efficiency