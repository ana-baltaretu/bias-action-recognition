#!/bin/bash
# --- General DAIC setup ---
#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --job-name=blender_render   # Job name
#SBATCH --output=/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/test_orbiting_green/blender_output_%j.log  # Output log file (%j will be replaced with job ID)
#SBATCH --error=/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/test_orbiting_green/blender_error_%j.log   # Error log file

# --- Setup specific for task ---
#SBATCH --ntasks=1                   # Number of tasks (1 task for this job)
#SBATCH --cpus-per-task=4            # Number of CPU cores per task
#SBATCH --time=02:00:00              # Maximum execution time (hh:mm:ss)
#SBATCH --mem=6144                   # Memory per node

# --- Email me when job finishes ---
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

start_time=$(date +%s)

animations=10
max_cubes=4

for cubes in $(seq 1 $max_cubes); do
  for red in $(seq 0 "$cubes"); do
    cbs=$((cubes-red))
    for green in $(seq 1 $cbs); do
      blue=$((cbs - green))
      blender --background --python ../cubes_experiment/cubes_orbiting_around_z.py -- --number "$cubes" --red "$red" --green "$green" --animations $animations\
      --save "/tudelft.net/staff-umbrella/StudentsCVlab/abaltaretu/test_orbiting_green/orbiting_${cubes}C${red}R${green}G${blue}B_pos"
      echo "Rendered 10 viewpoints for ${cubes} cubes (${red}R ${blue}B)"
    done
  done
done

end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"
