start_time=$(date +%s)

animations=10
max_cubes=4

#blender --background --python cubes_orbiting_around_z.py -- --number "$cubes" --red "$red" --green "$green" \
#  --animations $animations --save "./animation_output/actual_output/orbiting_green/orbiting_${cubes}C${red}R${green}G${blue}B_pos" &


### Actual script vvvvvvvv
for cubes in $(seq 1 $max_cubes); do
  for red in $(seq 0 "$cubes"); do
    cbs=$((cubes-red))
    for green in $(seq 1 $cbs); do
      blue=$((cbs - green))
      blender --background --python cubes_orbiting_around_z.py -- --number "$cubes" --red "$red" --green "$green" --animations $animations\
      --save "./animation_output/actual_output/orbiting_green/orbiting_${cubes}C${red}R${green}G${blue}B_pos" &
      wait
      echo "Rendered 10 viewpoints for ${cubes}cubes (${red}R${blue}B)"
    done
  done
done
### Actual script ^^^^^^^^


# Calculate the elapsed time in seconds
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"

