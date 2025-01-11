#!/bin/bash
#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --job-name=blender_render   # Job name
#SBATCH --output=blender_output_%j.log  # Output log file (%j will be replaced with job ID)
#SBATCH --error=blender_error_%j.log   # Error log file
#SBATCH --ntasks=1                   # Number of tasks (1 task for this job)
#SBATCH --cpus-per-task=4            # Number of CPU cores per task
#SBATCH --time=02:00:00              # Maximum execution time (hh:mm:ss)
#SBATCH --mem=6144                   # Memory per node

module load blender   # Load Blender module (if needed, depending on your system)

start_time=$(date +%s)

animations=10
max_cubes=4

for cubes in $(seq 1 $max_cubes); do
  for red in $(seq 0 "$cubes"); do
    cbs=$((cubes-red))
    for green in $(seq 1 $cbs); do
      blue=$((cbs - green))
      blender --background --python cubes_orbiting_around_z.py -- --number "$cubes" --red "$red" --green "$green" --animations $animations\
      --save "./animation_output/actual_output/orbiting_green/orbiting_${cubes}C${red}R${green}G${blue}B_pos"
      echo "Rendered 10 viewpoints for ${cubes} cubes (${red}R ${blue}B)"
    done
  done
done

end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"
