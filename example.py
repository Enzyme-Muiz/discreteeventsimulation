import simpy
import random
import pandas as pd

# List to store the data
queue_data = []

def patient(env, name, nurses, doctors, nurse_mean, nurse_std, doctor_mean, doctor_std):
    """
    Simulates a patient going through a nurse and then optionally a doctor.
    
    :param env: The SimPy environment.
    :param name: The name/ID of the patient.
    :param nurses: The resource representing the pool of nurses.
    :param doctors: The resource representing the pool of doctors.
    :param nurse_mean: The mean service time for the nurse.
    :param nurse_std: The standard deviation of the nurse's service time.
    :param doctor_mean: The mean service time for the doctor.
    :param doctor_std: The standard deviation of the doctor's service time.
    """
    with nurses.request() as request:
        yield request
        # Nurse service
        nurse_service_time = max(0, random.normalvariate(nurse_mean, nurse_std))
        yield env.timeout(nurse_service_time)
        print(f"Patient {name} finished with nurse at {env.now:.2f}")
    
    # 90% of patients proceed to see the doctor
    if random.uniform(0, 1) < 0.9:
        with doctors.request() as request:
            yield request
            # Doctor service
            doctor_service_time = max(0, random.normalvariate(doctor_mean, doctor_std))
            yield env.timeout(doctor_service_time)
            print(f"Patient {name} finished with doctor at {env.now:.2f}")

def generate_patients(env, nurses, doctors, interval_mean, interval_std, nurse_mean, nurse_std, doctor_mean, doctor_std):
    """
    Generate patients' entry and processing through a nurse and optionally a doctor.
    
    :param env: The SimPy environment.
    :param nurses: The resource representing the pool of nurses.
    :param doctors: The resource representing the pool of doctors.
    :param interval_mean: The mean interval between patient arrivals.
    :param interval_std: The standard deviation of the interval between patient arrivals.
    :param nurse_mean: The mean service time for the nurse.
    :param nurse_std: The standard deviation of the nurse's service time.
    :param doctor_mean: The mean service time for the doctor.
    :param doctor_std: The standard deviation of the doctor's service time.
    """
    patient_id = 0
    while True:
        # Generate the time interval for the next patient arrival
        time_interval = max(0, random.normalvariate(interval_mean, interval_std))
        
        # Wait for the next patient arrival
        yield env.timeout(time_interval)
        
        patient_id += 1
        print(f"Patient {patient_id} arrived at {env.now:.2f}")
        
        # Record queue lengths
        queue_data.append((env.now, len(nurses.queue), len(doctors.queue)))
        
        # Start the patient process
        env.process(patient(env, patient_id, nurses, doctors, nurse_mean, nurse_std, doctor_mean, doctor_std))

# Set up the environment
env = simpy.Environment()

# Create nurse and doctor resources
nurses = simpy.Resource(env, capacity=2)
doctors = simpy.Resource(env, capacity=1)

# Start the generate_patients process
env.process(generate_patients(env, nurses, doctors, interval_mean=5, interval_std=2, nurse_mean=20, nurse_std=1, doctor_mean=30, doctor_std=2))

# Run the simulation
env.run(until=200)

# Create a DataFrame from the collected data
df = pd.DataFrame(queue_data, columns=['time', 'nurse_queue', 'doctor_queue'])
print(df)
