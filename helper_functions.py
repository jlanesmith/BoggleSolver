
# Command-line functions to run to convert HEIC to jpg
# mkdir -p raw_data && for file in raw_data_heic/*.HEIC; do sips -s format jpeg "$file" --out "raw_data/$(basename "${file%.*}.jpg")"; done;


##################################################################################################
# Take in an array of numbers, in groups of consecutive numbers. For each group of consecutive   #
# numbers, calculate the average number. Return an array of the average number of each group,    #
# rounded to an integer. This is used to find lines to separate letters on the board.            #
##################################################################################################

def find_averages_of_groups(nums):
    # Initialize an empty list to store the averages
    averages = []
    
    # Start with the first number in the array
    start = 0
    
    # Traverse the array and find consecutive groups
    for i in range(1, len(nums)):
        # Check if the current number is not consecutive to the previous one
        if nums[i] != nums[i - 1] + 1:
            # If not consecutive, calculate the average of the current group
            group = nums[start:i]
            averages.append(int(sum(group) / len(group)))
            start = i  # Set the start of the next group
    
    # Don't forget to add the last group
    group = nums[start:]
    averages.append(int(sum(group) / len(group)))
    
    return averages
