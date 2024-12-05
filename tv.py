import streamlit as st
import csv
import random

# Streamlit Header
st.title("TV Program Scheduling with Genetic Algorithms")
st.write("Upload a CSV file with TV program ratings to generate an optimal schedule.")

# File Upload
uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    # Function to read the CSV file and convert it to a dictionary
    def read_csv_to_dict(file):
        program_ratings = {}
        reader = csv.reader(file)
        header = next(reader)  # Skip the header

        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # Convert ratings to floats
            program_ratings[program] = ratings

        return program_ratings

    # Read and display the uploaded file
    program_ratings_dict = read_csv_to_dict(uploaded_file)
    st.write("Uploaded Ratings Data:")
    st.json(program_ratings_dict)

    # Genetic Algorithm Parameters
    GEN = st.sidebar.slider("Generations", 50, 500, 100)
    POP = st.sidebar.slider("Population Size", 10, 100, 50)
    CO_R = st.sidebar.slider("Crossover Rate", 0.1, 1.0, 0.8)
    MUT_R = st.sidebar.slider("Mutation Rate", 0.1, 1.0, 0.2)
    EL_S = st.sidebar.slider("Elitism Size", 1, 10, 2)

    # Program data
    all_programs = list(program_ratings_dict.keys())
    all_time_slots = list(range(6, 24))

    # Fitness Function
    def fitness_function(schedule):
        total_rating = 0
        for time_slot, program in enumerate(schedule):
            total_rating += program_ratings_dict[program][time_slot]
        return total_rating

    # Initialize Population
    def initialize_population(programs, population_size):
        population = []
        for _ in range(population_size):
            random_schedule = random.sample(programs, len(programs))
            population.append(random_schedule)
        return population

    # Crossover
    def crossover(parent1, parent2):
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + [p for p in parent2 if p not in parent1[:point]]
        child2 = parent2[:point] + [p for p in parent1 if p not in parent2[:point]]
        return child1, child2

    # Mutation
    def mutate(schedule):
        idx1, idx2 = random.sample(range(len(schedule)), 2)
        schedule[idx1], schedule[idx2] = schedule[idx2], schedule[idx1]
        return schedule

    # Genetic Algorithm
    def genetic_algorithm(generations, population_size, crossover_rate, mutation_rate, elitism_size):
        population = initialize_population(all_programs, population_size)

        for _ in range(generations):
            population.sort(key=fitness_function, reverse=True)
            new_population = population[:elitism_size]

            while len(new_population) < population_size:
                parent1, parent2 = random.choices(population[:20], k=2)
                if random.random() < crossover_rate:
                    child1, child2 = crossover(parent1, parent2)
                else:
                    child1, child2 = parent1[:], parent2[:]

                if random.random() < mutation_rate:
                    child1 = mutate(child1)
                if random.random() < mutation_rate:
                    child2 = mutate(child2)

                new_population.extend([child1, child2])

            population = new_population[:population_size]

        return max(population, key=fitness_function)

    # Run the Genetic Algorithm
    if st.button("Generate Optimal Schedule"):
        optimal_schedule = genetic_algorithm(GEN, POP, CO_R, MUT_R, EL_S)

        # Display the results
        st.subheader("Optimal Schedule")
        for time_slot, program in enumerate(optimal_schedule):
            st.write(f"Time Slot {all_time_slots[time_slot]:02d}:00 - Program {program}")

        total_ratings = fitness_function(optimal_schedule)
        st.write(f"**Total Ratings**: {total_ratings}")
