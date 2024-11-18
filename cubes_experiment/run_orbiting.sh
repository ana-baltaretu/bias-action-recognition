start_time=$(date +%s)

animations=10
max_cubes=6

### Actual script vvvvvvvv
for cubes in $(seq 1 $max_cubes); do
  for red in $(seq 0 "$cubes"); do
    for i in $(seq 1 $animations); do
        blender --background --python red_blue_cubes_orbiting_around_z.py -- --number "$cubes" \
        --red "$red" --save "./animation_output/actual_output/orbiting/orbiting_${cubes}C${red}R${cubes-red}B_pos$i" &
    done
    wait
  done
done
### Actual script ^^^^^^^^


# Calculate the elapsed time in seconds
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$(( (elapsed_time % 3600) / 60 ))
seconds=$((elapsed_time % 60))
echo "Total execution time: ${minutes}m ${seconds}s"

