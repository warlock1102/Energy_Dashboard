def optimize_energy(household_data):
    # simple dummy logic: just return consumption as “charge”
    schedule = [{"charge": d["consumption"], "discharge": 0.0} for d in household_data]
    return schedule
