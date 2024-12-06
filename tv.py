import streamlit as st
import csv
import random

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # Convert the ratings to floats
            program_ratings[program] = ratings
    return program_ratings

# Path to the CSV file
file_path = "program_ratings1.csv"

# Get the data in the required format
program_ratings_dict = read_csv_to_dict(file_path)

# Sidebar for Genetic Algorithm Parameters
st.sidebar.title("Genetic Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate", min_value=0.0, max_value=0.95, value=0.8, step=0.01)
MUT_R = st.sidebar.slider("Mutation Rate", min_value=0.01, max_value=0.05, value=0.02, step=0.01)

ratings = program_ratings_dict
all_programs = list(ratings.keys())  # All programs
all_time_slots = list(range(6, 24))  # Time slots

# Fitness Function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

# Crossover
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutation
def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# Genetic Algorithm
def genetic_algorithm(initial_schedule, generations=100, population_size=50, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=2):
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population

    return population[0]

# Initialize Population
initial_schedule = random.sample(all_programs, len(all_programs))

# Run Genetic Algorithm
st.write("Running Genetic Algorithm with the following parameters:")
st.write(f"Crossover Rate: {CO_R}, Mutation Rate: {MUT_R}")

genetic_schedule = genetic_algorithm(initial_schedule)

# Ensure the schedule covers all time slots
if len(genetic_schedule) < len(all_time_slots):
    remaining_slots = len(all_time_slots) - len(genetic_schedule)
    genetic_schedule.extend(random.choices(all_programs, k=remaining_slots))

# Prepare the schedule for display
schedule_table = [
    {"Time Slot": f"{time_slot:02d}:00", "Program": genetic_schedule[i] if i < len(genetic_schedule) else "No Program"}
    for i, time_slot in enumerate(all_time_slots)
]

# Display Results in a Styled Table
table_html = "<table style='width:100%; border-collapse: collapse;'>"
table_html += "<tr style='background-color: #4CAF50; color: #fff;'><th>Time Slot</th><th>Program</th></tr>"

for time_slot, program in enumerate(genetic_schedule):
    # Alternate row colors for better readability
    row_color = "#330066" if time_slot % 2 == 0 else "#000000"
    time_label = f"{all_time_slots[time_slot]:02d}:00"
    table_html += f"<tr style='background-color: {row_color};'><td>{time_label}</td><td>{program}</td></tr>"

table_html += "</table>"

# Display the styled table in Streamlit
st.markdown(table_html, unsafe_allow_html=True)

# Display Total Ratings
st.write("Total Ratings:", fitness_function(genetic_schedule))
