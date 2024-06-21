# Step 1: Define the range of possible first terms and common ratios
first_term_range = range(10, 100)  # 2-digit numbers
common_ratio_range = range(2, 10)  # Common ratio should be a positive integer greater than 1

# Step 2: Generate the sequence for each possible first term and common ratio
for first_term in first_term_range:
    for common_ratio in common_ratio_range:
        # Generate the sequence
        sequence = [first_term * common_ratio**i for i in range(5)]
        
        # Step 3: Check if the sequence is valid (all terms are 2-digit numbers)
        if all(10 <= term <= 99 for term in sequence):
            # Step 4: Calculate the sum of the sequence
            sequence_sum = sum(sequence)
            
            # Step 5: Output the result
            print("The unique increasing geometric sequence is:", sequence)
            print("The sum of the sequence is:", sequence_sum)
            
            # Output the final numerical answer
            print(f"\\boxed{{{sequence_sum}}}")
            
            # Exit loop since the sequence is unique
            exit()