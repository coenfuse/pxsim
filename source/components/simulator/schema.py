# explain what this module does in 50 words
# ..



# standard imports
# ..

# internal imports
# ..

# component imports
# ..

# shared imports
# ..

# thirdparty imports
# ..



# ==============================================================================
# TODO : Created a new class to generate schema dictionaries due to default ref
# rencing of python variables. Would have required to do shallow_copy() or
# deep_copy() otherwise. Here we need to create a new schema factory instead and
# use the dictionary made from it as a response.
# ==============================================================================
# docs
# ------------------------------------------------------------------------------
def get_production_schema() -> dict:
    return {
        "production_name" : "",
        "production_count" : 0,
        "production_status" : 0,
        "production_cycle_time_s" : 0,
        "production_idle_limit_s" : 0,
        "production_last_cycle_s" : 0
    }

    
# docs
# ------------------------------------------------------------------------------
def get_machine_schema() -> dict:
    return {
        "machine_name" : "",
        "machine_status" : "",
        "production_list" : [],
        "production_count": 0
    }


# docs
# ------------------------------------------------------------------------------
def get_simulation_schema() -> dict:
    return {
        "machine_list" : [],
        "active_machines" : 0
    }